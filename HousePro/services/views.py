from django import forms
from django.contrib.auth import get_user_model, authenticate, login, logout
from .models import Category, State, Order, User, Notification, Review
from .forms import UserRegistrationForm, MasterRegistrationForm, OrderForm, ReviewForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import stripe
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth import get_backends

def home(request):
    return render(request, 'home.html')

def register(request):
    states = State.objects.all()  
    categories = Category.objects.all() 
    form = UserRegistrationForm()
    master_form = MasterRegistrationForm()

    if request.method == 'POST':
        user_type = request.POST.get('user_type')  
        
        if user_type == 'normal':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1']) 
                user.save()

                # Explicitly specify the backend
                backend = get_backends()[0]
                user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
                
                login(request, user)  
                messages.success(request, 'Registration successful! You are now logged in.')
                return redirect('user_page')
            else:
                messages.error(request, 'There was an error with your registration form.')

        elif user_type == 'master':
            master_form = MasterRegistrationForm(request.POST)
            if master_form.is_valid():
                user = master_form.save(commit=False)
                user.set_password(master_form.cleaned_data['password1'])  
                user.is_master = True  
                user.save()
                master_form.save_m2m()  

                # Explicitly specify the backend
                backend = get_backends()[0]
                user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
                
                login(request, user)  
                messages.success(request, 'Registration successful! You are now logged in.')
                return redirect('master_page')
            else:
                messages.error(request, 'There was an error with your master registration form.')

    return render(request, 'register.html', {
        'form': form, 
        'master_form': master_form, 
        'states': states, 
        'categories': categories 
    })

import logging

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')

            # Redirect based on whether the user is a master or a regular user
            if user.is_master:  
                return redirect('master_page')  
            else:
                return redirect('user_page')  
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

@login_required  
def logout_view(request):
    logout(request)  
    messages.success(request, 'You have been logged out successfully.')  
    return redirect('home')  

def login_redirect_view(request):
    if request.user.is_authenticated:
        if request.user.is_master:
            return redirect('master_page')
        else:
            return redirect('user_page')
    else:
        return redirect('login')

def user_page_view(request):
    search_term = request.GET.get('search_query', '')
    category_filter = request.GET.get('category_filter', '')
    state_filter = request.GET.get('state_filter', '')
    experience_filter = request.GET.get('experience_filter', None)
    reviews_filter = request.GET.get('reviews_filter', None)
    completed_orders_filter = request.GET.get('completed_orders_filter', None)

    top_masters = User.objects.filter(is_master=True).order_by('id')

    if search_term:
        top_masters = top_masters.filter(
            Q(username__icontains=search_term) | 
            Q(categories__name__icontains=search_term)
        )

    if category_filter:
        top_masters = top_masters.filter(categories__id=category_filter)

    if state_filter:
        top_masters = top_masters.filter(state__id=state_filter)

    if experience_filter:
        try:
            experience = int(experience_filter)
            top_masters = top_masters.filter(experience__gte=experience)
        except ValueError:
            pass

    if reviews_filter:
        top_masters = top_masters.annotate(num_reviews=Count('master_orders__to_master_review')).filter(num_reviews__gte=reviews_filter)

    top_masters = top_masters.annotate(
        num_completed_orders=Count('master_orders', filter=Q(master_orders__status='completed'))
    )

    if completed_orders_filter:
        top_masters = top_masters.filter(num_completed_orders__gte=completed_orders_filter)

    paginator = Paginator(top_masters, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'states': State.objects.all(),
    }

    return render(request, 'user_page.html', context)

@login_required
def master_page_view(request):
    categories = Category.objects.all()
    states = State.objects.all()
    available_orders = Order.objects.filter(status='pending', master__isnull=True).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    total_orders = Order.objects.filter(master=request.user).count()
    avg_order_price = Order.objects.filter(master=request.user).aggregate(Avg('price'))['price__avg'] or 0

    context = {
        'user': request.user,
        'available_orders': available_orders,
        'notifications': notifications,
        'total_orders': total_orders,
        'categories': categories, 
        'states': states,
        'avg_order_price': round(avg_order_price, 2),
    }

    return render(request, 'master_page.html', context)

@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)  
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user  
            order.status = 'Pending' 
            order.save()
            
            notification = Notification.objects.create(
                user=request.user,
                message=f"You have successfully created a new order: {order.order_name}.",
                notification_type='order_created'
            )
            notification.send_email_notification() 

            messages.success(request, 'Order created successfully!')
            return redirect('user_page')
        else:
            messages.error(request, 'Error in form submission.')
    else:
        form = OrderForm()

    categories = Category.objects.all()
    states = State.objects.all()

    return render(request, 'create_order.html', {
        'form': form,
        'categories': categories,
        'states': states
    })

def leave_review(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status.lower() != 'completed':
        return render(request, 'leave_review.html', {
            'order': order,
            'error': 'You can only leave a review for completed orders.',
            'rating_range': range(1, 11)  
        })

    if order.review:
        return render(request, 'leave_review.html', {
            'order': order,
            'error': 'You have already reviewed this order.',
            'rating_range': range(1, 11)  
        })

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.user = request.user
            review.save()
            order.review = review  
            order.save()

            Notification.objects.create(
                user=request.user,
                notification_type='review_created',
                message=f'You have successfully left a review for order: {order.order_name}',
            )

            if order.master:
                Notification.objects.create(
                    user=order.master,
                    notification_type='review_received',
                    message=f'You have received a new review for order: {order.order_name}',
                )

            return render(request, 'leave_review.html', {
                'order': order,
                'success': 'Review submitted successfully!',
                'rating_range': range(1, 11)  
            })
        else:
            return render(request, 'leave_review.html', {
                'order': order,
                'error': form.errors.as_json(),
                'rating_range': range(1, 11)  
            })

    return render(request, 'leave_review.html', {
        'order': order,
        'rating_range': range(1, 11)  
    })

def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

@login_required
def accept_order(request, order_id):
    if request.method == 'POST' and request.is_ajax():
        order = get_object_or_404(Order, id=order_id)

        if order.master is None and order.status == 'pending':
            order.master = request.user
            order.status = 'confirmed'
            order.save()

            Notification.objects.create(
                user=order.user,
                message=f"Your order has been accepted by {request.user.username}. Please proceed with the payment.",
                notification_type='order_accepted'
            )

            Notification.objects.create(
                user=request.user,
                message=f"You have successfully accepted the order from {order.user.username}. The order status is now confirmed.",
                notification_type='order_accepted'
            )

            return JsonResponse({'status': 'success', 'message': 'Order accepted successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'This order has already been accepted or is not pending.'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def order_payment(request, order_id):
    order = Order.objects.get(id=order_id)
    # Payment logic...

    user_notification = Notification.objects.create(
        user=order.user,
        message=f"You have successfully paid for the order {order.order_name}.",
        notification_type='order_paid'
    )
    user_notification.send_email_notification()

    master_notification = Notification.objects.create(
        user=order.master,
        message=f"The order {order.order_name} has been paid by {order.user.username}.",
        notification_type='order_paid'
    )
    master_notification.send_email_notification()

    return redirect('order_detail', order_id=order.id)

def complete_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'Completed'
    order.save()

    user_notification = Notification.objects.create(
        user=order.user,
        message=f"The order {order.order_name} has been marked as completed by {order.master.username}. Please leave a review.",
        notification_type='order_completed'
    )
    user_notification.send_email_notification()

    master_notification = Notification.objects.create(
        user=order.master,
        message=f"You have marked the order {order.order_name} as completed.",
        notification_type='order_completed'
    )
    master_notification.send_email_notification()

    return redirect('master_dashboard')

@login_required
def user_dashboard_view(request):
    user = request.user
    total_orders = Order.objects.filter(user=user).count()

    context = {
        'user': user,
        'total_orders': total_orders,
    }
    return render(request, 'user_dashboard.html', context)

@login_required
def master_dashboard_view(request):
    master = request.user
    available_orders = Order.objects.filter(status='Pending')
    past_orders = Order.objects.filter(master=master, status__in=['Completed', 'Canceled'])

    category_filter = request.GET.get('category')
    urgency_filter = request.GET.get('urgency')

    if category_filter:
        available_orders = available_orders.filter(category__id=category_filter)
    if urgency_filter:
        available_orders = available_orders.filter(urgency=urgency_filter)

    categories = Category.objects.all()

    context = {
        'available_orders': available_orders,
        'past_orders': past_orders,
        'categories': categories,
    }
    return render(request, 'master_dashboard.html', context)

@login_required
def orders_view(request):
    if request.user.is_master:
        orders = Order.objects.filter(master=request.user).order_by('-date')
        template_name = 'master_orders.html'
    else:   
        orders = Order.objects.filter(user=request.user).order_by('-date')
        template_name = 'user_orders.html'

    context = {
        'orders': orders,
        'notifications': Notification.objects.filter(user=request.user, is_read=False),
    }
    return render(request, template_name, context)

@login_required
def available_orders_view(request):
    orders = Order.objects.filter(status='pending')
    search_query = request.GET.get('search_query', '')
    category_filter = request.GET.get('category_filter', '')
    state_filter = request.GET.get('state_filter', '')
    price_filter = request.GET.get('price_filter', '')
    urgency_filter = request.GET.get('urgency_filter', '')

    if search_query:
        orders = orders.filter(order_name__icontains=search_query)

    if category_filter:
        orders = orders.filter(category__id=category_filter)

    if state_filter:
        orders = orders.filter(state__id=state_filter)

    if price_filter:
        try:
            price = float(price_filter)
            orders = orders.filter(price__gte=price)
        except ValueError:
            pass

    if urgency_filter:
        orders = orders.filter(urgency=urgency_filter)

    paginator = Paginator(orders, 6)  
    page_number = request.GET.get('page')
    available_orders = paginator.get_page(page_number)

    context = {
        'available_orders': available_orders,
        'categories': Category.objects.all(),
        'states': State.objects.all(),
    }
    
    return render(request, 'master_orders.html', context)

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifications.update(is_read=True)
    
    context = {
        'notifications': notifications
    }
    
    if request.user.is_master:
        return render(request, 'notifications/master_notifications.html', context)
    else:
        return render(request, 'notifications/user_notifications.html', context)

def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': order.order_name,
                    },
                    'unit_amount': int(order.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payment_success/'),
            cancel_url=request.build_absolute_uri('/payment_cancel/'),
        )
        return JsonResponse({'id': session.id})

    return render(request, 'checkout.html', {
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_cancel(request):
    return render(request, 'payment_cancel.html')

def submit_review(request, order_id):
    order = Order.objects.get(id=order_id)

    # Notify the master of the review
    review_notification = Notification.objects.create(
        user=order.master,
        message=f"You have received a new review from {order.user.username}.",
        notification_type='review_submitted'
    )
    review_notification.send_email_notification()

    return redirect('user_dashboard')
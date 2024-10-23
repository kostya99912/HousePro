from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from services import views
from services.views import (
    register, login_view, logout_view, login_redirect_view,
    user_page_view, master_page_view, user_dashboard_view,
    master_dashboard_view, create_order, notifications_view,
    orders_view, leave_review
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('login_redirect/', login_redirect_view, name='login_redirect'),

    # User and Master Pages
    path('', views.home, name='home'),
    path('user_page/', user_page_view, name='user_page'),
    path('master_page/', master_page_view, name='master_page'),
    path('user_dashboard/', user_dashboard_view, name='user_dashboard'),
    path('master_dashboard/', master_dashboard_view, name='master_dashboard'),

    # Orders
    path('create_order/', create_order, name='create_order'),
    path('user_orders/', orders_view, name='user_orders'),
    path('leave_review/<int:order_id>/', leave_review, name='leave_review'),
    path('accept_order/<int:order_id>/', views.accept_order, name='accept_order'),
    
    # Notifications
    path('notifications/', notifications_view, name='notifications'),

    # Payment
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'),

    # Social Auth
    path('oauth/', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
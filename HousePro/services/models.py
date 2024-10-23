from django.db import models
from datetime import date
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.mail import send_mail
from django.db.models import Avg

# State Model
class State(models.Model):
    code = models.CharField(max_length=2, unique=True)  
    name = models.CharField(max_length=20)  
    def __str__(self):
        return self.name

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=15, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Custom User Model
class User(AbstractUser):
    is_master = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=15, null=True, blank=True)
    last_name = models.CharField(max_length=15, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    average_rating = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return self.username

# Order Model
class Order(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_orders')
    master = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='master_orders')
    order_name = models.CharField(max_length=30, verbose_name="Short Order Name")
    description = models.TextField(max_length=500, verbose_name="Full Order Description")
    date = models.DateField(default=date.today, verbose_name="Proposed Date")
    urgency = models.CharField(max_length=6, choices=PRIORITY_CHOICES, verbose_name="Urgency Level")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Proposed Price")
    location = models.CharField(max_length=20, verbose_name="City")
    state = models.ForeignKey(State, on_delete=models.PROTECT, verbose_name="State")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Task Category")
    photos = models.ImageField(upload_to='order_photos/', blank=True, null=True, verbose_name="Attach Photos")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name="Order Status")
    user_comments = models.TextField(blank=True, null=True, verbose_name="User Comments")
    master_comments = models.TextField(blank=True, null=True, verbose_name="Master Comments")
    review = models.OneToOneField('Review', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Order Review", related_name='order_review')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.order_name}"

# Review Model
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_review')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='to_master_review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)], verbose_name="Rating (1-10)")
    comment = models.TextField(blank=True, null=True, verbose_name="Comment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'order')

    def __str__(self):
        return f"Review by {self.user.username} for Order {self.order.id} - Rating: {self.rating}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  
        master = self.order.master
        if master:
            avg_rating = Review.objects.filter(order__master=master).aggregate(Avg('rating'))['rating__avg']
            master.average_rating = avg_rating
            master.save()

# Notification Model
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('order_status', 'Order Status Update'),
        ('payment', 'Payment Update'),
        ('new_order', 'New Order Available'),
        ('review', 'New Review Received'),
        ('general', 'General Notification'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.created_at}"

    def send_email_notification(self):
        subject = f"New {self.get_notification_type_display()} Notification"
        message = self.message
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.user.email]

        send_mail(subject, message, from_email, recipient_list)






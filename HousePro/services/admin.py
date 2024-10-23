from django.contrib import admin

from .models import User, Order, Review, State, Category, Notification

# Register your models here
admin.site.register(User)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(State)
admin.site.register(Notification)
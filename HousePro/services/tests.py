from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Order, Category, State
from random import choice

class OrderCreateTest(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username='testuser', password='password123'
        )
        self.client.login(username='testuser', password='password123')
        
        # Fetch existing categories and states
        categories = Category.objects.all()
        states = State.objects.all()

        # Ensure there are existing categories and states
        if not categories.exists() or not states.exists():
            raise ValueError("There must be existing categories and states for this test to run")
        
        # Randomly pick from existing categories and states
        self.category = choice(categories)
        self.state = choice(states)
    
    def test_create_order(self):
        # Prepare the data for the new order
        data = {
            'order_name': 'Fix my sink',
            'description': 'The kitchen sink is leaking and needs repair.',
            'category': self.category.id,  # Use existing category
            'state': self.state.id,  # Use existing state
            'price': '100.00',
            'date': '2024-10-20',
            'urgency': 'medium',
            'location': 'London'
        }
        
        # Send a POST request to create the order
        response = self.client.post(reverse('create_order'), data)
        
        # Check if the order was created successfully and user is redirected
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Order.objects.filter(order_name='Fix my sink').exists())
        self.assertEqual(Order.objects.count(), 1)
        
        order = Order.objects.first()
        
        # Ensure the order data matches the input
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.category, self.category)
        self.assertEqual(order.state, self.state)
        self.assertEqual(order.status, 'Pending')
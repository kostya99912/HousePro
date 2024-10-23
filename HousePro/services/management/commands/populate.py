from django.core.management.base import BaseCommand
from services.models import User, Order, Category, State
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Delete user orders and create new completed orders for testing'

    def handle(self, *args, **kwargs):
        # Get user with username "user"
        try:
            user = User.objects.get(username="user")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User with username 'user' does not exist."))
            return

        # Delete all orders
        orders_to_delete = Order.objects.filter(user=user)
        deleted_count = orders_to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count[0]} orders for user {user.username}."))

        # Get sates and categories
        categories = Category.objects.all()
        states = State.objects.all()

        # Create new orders
        for i in range(5):  
            category = random.choice(categories)
            state = random.choice(states)

            new_order = Order.objects.create(
                user=user,
                master=None,  # Not accepted by master
                order_name=f"New Order {i+1} by {user.username}",
                description=f"Completed order description {i+1}",
                price=random.uniform(50.00, 500.00),
                category=category,
                state=state,
                urgency=random.choice(['low', 'medium', 'high']),
                status="completed",  # Status as "completed"
                location=f"City {i+1}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            self.stdout.write(self.style.SUCCESS(f"Created new order {new_order.order_name} with status 'completed'."))






# from django.core.management.base import BaseCommand
# from faker import Faker
# import random
# from services.models import User, State, Category, Order, Review
# from django.contrib.auth import get_user_model
# from decimal import Decimal

# class Command(BaseCommand):
#     help = 'Populates the database with fake users, masters, orders, and reviews'

#     def handle(self, *args, **kwargs):
#         fake = Faker()
#         User = get_user_model()

#         # Fetch all existing categories and states
#         categories = Category.objects.all()
#         states = State.objects.all()

#         if not categories.exists() or not states.exists():
#             self.stdout.write(self.style.ERROR("Categories and States must exist in the database before running this command."))
#             return

#         # Create 10 fake users and masters
#         for _ in range(10):
#             is_master = random.choice([True, False])
#             first_name = fake.first_name()[:15]  # Limit first name to 15 characters
#             last_name = fake.last_name()[:15]    # Limit last name to 15 characters
#             email = fake.unique.email()          # Ensure unique email
#             state = random.choice(states)
            
#             user = User.objects.create_user(
#                 username=fake.user_name()[:15],  # Username limited to 15 characters
#                 email=email,
#                 password="password123",
#                 first_name=first_name,
#                 last_name=last_name,
#                 is_master=is_master,
#                 state=state,
#                 experience=random.randint(1, 10) if is_master else None
#             )
            
#             # If the user is a master, assign random categories
#             if is_master:
#                 categories_to_assign = random.sample(list(categories), random.randint(1, 3))
#                 user.categories.set(categories_to_assign)

#         # Create 20 fake orders
#         for _ in range(20):
#             user = random.choice(User.objects.filter(is_master=False))
#             master = random.choice(User.objects.filter(is_master=True))
#             category = random.choice(categories)
#             state = random.choice(states)

#             order = Order.objects.create(
#                 user=user,
#                 master=master,
#                 order_name=fake.sentence(nb_words=3)[:30],  # Limit to 30 characters
#                 description=fake.text(max_nb_chars=500),    # Limit to 500 characters
#                 date=fake.date_this_year(),
#                 urgency=random.choice(['low', 'medium', 'high']),
#                 price=Decimal(f'{random.uniform(50, 500):.2f}'),  # Price between 50 and 500
#                 location=fake.city()[:20],  # City name limited to 20 characters
#                 state=state,
#                 category=category,
#                 status=random.choice(['pending', 'confirmed', 'in_progress', 'completed', 'canceled'])
#             )

#             # Create a review if the order is completed
#             if order.status == 'completed':
#                 Review.objects.create(
#                     user=user,
#                     order=order,
#                     rating=random.randint(1, 10),
#                     comment=fake.text(max_nb_chars=300)  # Limit comment to 300 characters
#                     )

#             self.stdout.write(self.style.SUCCESS("Fake users, masters, and orders created successfully!"))
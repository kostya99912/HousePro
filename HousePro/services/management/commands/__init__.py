from django.core.management.base import BaseCommand
from services.models import User
from faker import Faker
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Populate the database with fake masters'

    def handle(self, *args, **kwargs):
        fake = Faker()
        for _ in range(100):
            username = fake.user_name()
            password = make_password('password123')  
            profile_picture = fake.image_url()  
            User.objects.create(username=username, password=password, is_master=True, profile_picture=profile_picture)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated 100 masters!'))
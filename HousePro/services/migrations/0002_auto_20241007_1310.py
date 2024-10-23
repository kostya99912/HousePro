# your_app/migrations/0002_auto_<timestamp>.py

from django.db import migrations

def add_states(apps, schema_editor):
    State = apps.get_model('services', 'State')  # Change to your actual model name
    states = [
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'),
    ]
    State.objects.bulk_create([State(code=code, name=name) for code, name in states])

def add_categories(apps, schema_editor):
    Category = apps.get_model('services', 'Category')  # Change to your actual model name
    categories = [
        ('Plumbing', 'Plumbing services'),
        ('Electrical', 'Electrical services'),
        ('Cleaning', 'Home and office cleaning'),
        ('Carpentry', 'Woodwork and carpentry'),
        ('Painting', 'House painting and decoration'),
        ('Landscaping', 'Garden and landscaping services'),
        ('Tiling', 'Tile installation and repairs'),
        ('HVAC', 'Heating, ventilation, and air conditioning services'),
        ('Fencing', 'Fence installation and repair'),
        ('Roofing', 'Roof repairs and installations'),
    ]
    Category.objects.bulk_create([Category(name=name, description=description) for name, description in categories])

class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),  # Change to your last migration file
    ]

    operations = [
        migrations.RunPython(add_states),
        migrations.RunPython(add_categories),
    ]
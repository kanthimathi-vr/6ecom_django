# store/management/commands/generate_products.py
from django.core.management.base import BaseCommand
from store.models import Category, Product
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Generates 50 dummy products and 4 categories.'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # 1. Clear existing products (optional, for fresh runs)
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing Products and Categories.'))

        # 2. Create Categories
        category_names = ['Electronics', 'Books', 'Apparel', 'Home Goods']
        categories = []
        for name in category_names:
            category, created = Category.objects.get_or_create(
                name=name, 
                slug=name.lower().replace(' ', '-')
            )
            categories.append(category)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories.'))

        # 3. Create 50 Products
        products_to_create = []
        for i in range(50):
            product = Product(
                name=fake.catch_phrase(),
                price=round(random.uniform(10.00, 500.00), 2),
                # Assign a random category from the list
                category=random.choice(categories), 
                digital=random.choice([True, False]),
            )
            products_to_create.append(product)

        Product.objects.bulk_create(products_to_create)

        self.stdout.write(self.style.SUCCESS('Successfully generated 50 dummy products.'))


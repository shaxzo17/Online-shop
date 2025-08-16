import csv
from django.core.management.base import BaseCommand
from store.models import Product, Category

class Command(BaseCommand):
    help = "Import products from a CSV file"

    def handle(self, *args, **kwargs):
        with open('products.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category, _ = Category.objects.get_or_create(name=row['category'])
                Product.objects.create(
                    name=row['name'],
                    price=row['price'],
                    category=category,
                    image=row['image'],
                    description=row['description']
                )
        self.stdout.write(self.style.SUCCESS("Successfully imported products!"))

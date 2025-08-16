import csv
import os
from django.core.files import File
from store.models import Product, Category
from django.conf import settings

def run():
    file_path = os.path.join(settings.BASE_DIR, 'data', 'products.csv')

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category, created = Category.objects.get_or_create(name=row['category'])
            product = Product(
                name=row['name'],
                price=row['price'],
                description=row['description'],
                category=category
            )
            # Rasmni yuklash
            image_path = os.path.join(settings.BASE_DIR, 'media', 'products', row['image'])
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img:
                    product.image.save(row['image'], File(img), save=True)

            product.save()
            print(f"Mahsulot qo'shildi: {product.name}")

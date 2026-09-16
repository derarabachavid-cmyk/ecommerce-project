from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from store.models import Category, Product


class Command(BaseCommand):
    help = "Safely seed store data and assign product images."

    def handle(self, *args, **options):

        categories = {
            "Electronics": "Modern electronic devices and accessories.",
            "Fashion": "Stylish clothing, shoes, and fashion products.",
            "Home": "Useful products for your home and workspace.",
            "Accessories": "Practical and stylish everyday accessories.",
        }

        category_objects = {}

        for name, description in categories.items():
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            category_objects[name] = category

            self.stdout.write(
                f"{'Created' if created else 'Already exists'} category: {name}"
            )

        products = [
            ("Wireless Headphones", "High-quality wireless headphones with clear sound and comfortable everyday listening.", "59.99", 20, "Electronics", "headphone.png"),
            ("Smart Watch Pro", "Modern smart watch with a stylish design and useful everyday features.", "89.99", 15, "Electronics", "smart_watch.png"),
            ("Bluetooth Speaker", "Portable Bluetooth speaker with powerful sound.", "39.99", 25, "Electronics", "speaker.png"),
            ("Wireless Mouse", "Comfortable wireless mouse for smooth computer use.", "24.99", 30, "Electronics", "mouse.png"),
            ("Mechanical Keyboard", "Responsive mechanical keyboard for work and gaming.", "69.99", 18, "Electronics", "keyboard.png"),

            ("Classic Sneakers", "Comfortable everyday sneakers with a clean design.", "64.99", 20, "Fashion", "shoes.png"),
            ("Casual Hoodie", "Comfortable casual hoodie suitable for everyday wear.", "44.99", 25, "Fashion", "she.png"),
            ("Premium Backpack", "Durable backpack for school, work, and travel.", "54.99", 20, "Fashion", "bag.png"),
            ("Classic Denim Jacket", "Timeless denim jacket with a versatile style.", "59.99", 15, "Fashion", "jacket.png"),
            ("Cotton T-Shirt", "Soft cotton T-shirt with a simple comfortable design.", "19.99", 40, "Fashion", "t-shirt.png"),

            ("Modern Desk Lamp", "Modern desk lamp for work and study.", "34.99", 25, "Home", "lamp.png"),
            ("Insulated Water Bottle", "Reusable insulated bottle for everyday use.", "22.99", 35, "Home", "botle.png"),
            ("Minimalist Desk Organizer", "Simple organizer for a clean workspace.", "17.99", 30, "Home", "med.png"),
            ("LED Night Light", "Compact LED night light with a modern design.", "14.99", 35, "Home", "ligt.png"),
            ("Portable Coffee Maker", "Compact coffee maker for convenient coffee preparation.", "79.99", 12, "Home", "coffee.png"),

            ("Premium Leather Wallet", "Elegant leather wallet with multiple card slots.", "29.99", 25, "Accessories", "walet.png"),
            ("Classic Sunglasses", "Stylish sunglasses with a comfortable frame.", "24.99", 30, "Accessories", "glasses.png"),
            ("Stainless Steel Watch", "Modern stainless steel watch with a clean design.", "49.99", 15, "Accessories", "watch.png"),
            ("Canvas Belt", "Durable casual canvas belt with a strong buckle.", "19.99", 35, "Accessories", "belt.png"),
            ("Travel Key Organizer", "Compact key organizer for keeping keys neat.", "14.99", 40, "Accessories", "bag.png"),
        ]

        media_root = Path(settings.MEDIA_ROOT)

        for name, description, price, stock, category_name, image in products:

            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": Decimal(price),
                    "stock": stock,
                    "category": category_objects[category_name],
                    "image": f"products/{image}",
                },
            )

            # Only assign an image if the product currently has none.
            # Existing product information is not overwritten.
            if not product.image:

                image_path = media_root / "products" / image

                if image_path.exists():
                    product.image = f"products/{image}"
                    product.save(update_fields=["image"])

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Image assigned: {name} -> {image}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Image missing: {image}"
                        )
                    )

            self.stdout.write(
                f"{'Created' if created else 'Already exists'} product: {name}"
            )

        # Fix the two products that were assigned the wrong image
        fixes = {
            "LED Night Light": "ligt.png",
            "Stainless Steel Watch": "watch.png",
        }

        for product_name, image in fixes.items():

            product = Product.objects.get(name=product_name)
            image_path = media_root / "products" / image

            if image_path.exists():
                product.image = f"products/{image}"
                product.save(update_fields=["image"])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Fixed image: {product_name} -> {image}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Categories: {Category.objects.count()} | "
                f"Products: {Product.objects.count()}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS("No existing data was deleted.")
        )
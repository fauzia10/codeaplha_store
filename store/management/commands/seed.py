from django.core.management.base import BaseCommand
from store.models import User, Product

class Command(BaseCommand):
    help = 'Seeds database with initial users and products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # 1. Create superuser
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@aurastore.com',
                password='admin123',
                phone_number='1234567890',
                address='123 Admin Lane'
            )
            self.stdout.write(self.style.SUCCESS('Superuser "admin" created successfully (Password: admin123)'))
        else:
            self.stdout.write('Superuser "admin" already exists.')

        # 2. Create customer user
        if not User.objects.filter(username='buyer').exists():
            customer_user = User.objects.create_user(
                username='buyer',
                email='buyer@aurastore.com',
                password='buyer123',
                phone_number='0987654321',
                address='456 Customer Street'
            )
            self.stdout.write(self.style.SUCCESS('Customer user "buyer" created successfully (Password: buyer123)'))
        else:
            self.stdout.write('Customer user "buyer" already exists.')

        # 3. Create products
        products_data = [
            {
                'name': 'Aura Mechanical Keyboard',
                'description': 'A premium minimalist mechanical keyboard featuring custom tactile brown switches, keycaps designed for peak acoustics, and a warm-white backlighting system housed in a CNC aluminum frame.',
                'price': 149.99,
                'stock': 12,
                'image': 'products/keyboard.png'
            },
            {
                'name': 'Aura Sound Headset',
                'description': 'A sleek studio-grade over-ear wireless headphone featuring advanced active noise cancellation, custom audio profiles, and ultra-plush memory foam ear cups.',
                'price': 299.99,
                'stock': 8,
                'image': 'products/headset.png'
            },
            {
                'name': 'Aura Minimalist Lamp',
                'description': 'A sculptural warm-glow desk lamp built from solid ash wood and brushed aluminum. Touch controls allow seamless dimming for perfect late-night workspace lighting.',
                'price': 89.99,
                'stock': 4,
                'image': 'products/lamp.png'
            }
        ]

        for p_info in products_data:
            product, created = Product.objects.update_or_create(
                name=p_info['name'],
                defaults={
                    'description': p_info['description'],
                    'price': p_info['price'],
                    'stock': p_info['stock'],
                    'image': p_info['image']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                self.stdout.write(f'Updated product: {product.name}')

        self.stdout.write(self.style.SUCCESS('Database seeding completed.'))

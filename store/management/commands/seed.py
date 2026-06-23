from django.core.management.base import BaseCommand
from store.models import User, Product


class Command(BaseCommand):
    help = 'Seeds database with initial users and products (INR pricing)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # ── 1. Superuser ──────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@aurastore.com',
                password='admin123',
                phone_number='9999999999',
                address='123 Admin Lane, New Delhi'
            )
            self.stdout.write(self.style.SUCCESS('Superuser "admin" created (Password: admin123)'))
        else:
            self.stdout.write('Superuser "admin" already exists.')

        # ── 2. Sample customer ────────────────────────────────────
        if not User.objects.filter(username='buyer').exists():
            User.objects.create_user(
                username='buyer',
                email='buyer@aurastore.com',
                password='buyer123',
                phone_number='9876543210',
                address='456 Customer Street, Mumbai'
            )
            self.stdout.write(self.style.SUCCESS('Customer "buyer" created in SQLite (Password: buyer123)'))
        else:
            self.stdout.write('Customer "buyer" already exists in SQLite.')

        # Register same customer in MongoDB for front-end customer auth
        try:
            from store.mongo_auth import register_user
            mongo_result = register_user('buyer', 'buyer@aurastore.com', 'buyer123')
            if mongo_result.get('success'):
                self.stdout.write(self.style.SUCCESS('Customer "buyer" registered in MongoDB.'))
            else:
                self.stdout.write(f'MongoDB seeding: {mongo_result.get("error")}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not seed buyer in MongoDB: {e}'))

        # ── 3. Products ───────────────────────────────────────────
        self.stdout.write('Clearing existing products...')
        Product.objects.all().delete()

        products_data = [

            # ── Electronics ────────────────────────────────────
            {
                'name': 'Aura Mechanical Keyboard',
                'description': (
                    'A premium minimalist mechanical keyboard featuring custom tactile brown switches, '
                    'keycaps designed for peak acoustics, and warm-white backlighting housed in a '
                    'CNC-machined aluminium frame. Plug-and-play USB-C with N-Key rollover.'
                ),
                'price': 12999.00,
                'stock': 12,
                'category': 'Electronics',
                'image': 'products/keyboard.png',
            },
            {
                'name': 'Aura Ergonomic Mouse',
                'description': (
                    'A high-precision 4000 DPI wireless mouse with a sculpted ergonomic grip, '
                    'silent magnetic clicks, aluminium scroll wheel, and 80-hour battery life. '
                    '2.4 GHz nano-receiver and USB-C fast charge.'
                ),
                'price': 6499.00,
                'stock': 18,
                'category': 'Electronics',
                'image': 'products/mouse.png',
            },
            {
                'name': 'Aura Monitor Stand',
                'description': (
                    'A minimalist solid walnut and brushed-steel monitor riser that elevates your '
                    'display to the perfect eye-level. Hidden cable management channel keeps your '
                    'desk spotless. Supports monitors up to 32".'
                ),
                'price': 9799.00,
                'stock': 7,
                'category': 'Electronics',
                'image': 'products/monitor_stand.png',
            },
            {
                'name': 'Aura USB-C Hub (7-in-1)',
                'description': (
                    '7-in-1 aluminium USB-C hub with 4K HDMI, 100W PD pass-through, '
                    '2× USB-A 3.0, SD/MicroSD card slots, and Gigabit Ethernet. '
                    'Compact palm-sized form that travels anywhere.'
                ),
                'price': 3299.00,
                'stock': 25,
                'category': 'Electronics',
                'image': 'products/usb_hub.png',
            },

            # ── Desk Mats ──────────────────────────────────────
            {
                'name': 'Aura Leather Desk Pad',
                'description': (
                    'Premium full-grain black leather desk pad with micro-stitched edges and a '
                    'non-slip cork base. 90 × 40 cm — perfectly sized to anchor your keyboard '
                    'and mouse with a silky-smooth writing surface.'
                ),
                'price': 3999.00,
                'stock': 22,
                'category': 'Desk Mats',
                'image': 'products/desk_pad.png',
            },
            {
                'name': 'Aura XL Microfibre Desk Mat',
                'description': (
                    'Extra-large 120 × 60 cm desk mat in deep obsidian charcoal microfibre. '
                    'Ultra-thick 4 mm foam core for wrist comfort, stitched edges, and a '
                    'rubberised base that never slides.'
                ),
                'price': 2499.00,
                'stock': 30,
                'category': 'Desk Mats',
                'image': 'products/desk_mat_xl.png',
            },
            {
                'name': 'Aura Cork Desk Pad',
                'description': (
                    'Eco-friendly natural cork desk pad (80 × 35 cm) with a linen surface layer. '
                    'Self-healing, antimicrobial, and 100% sustainable. Pairs beautifully with '
                    'minimal Scandinavian desk setups.'
                ),
                'price': 1799.00,
                'stock': 15,
                'category': 'Desk Mats',
                'image': 'products/cork_pad.png',
            },

            # ── Audio ──────────────────────────────────────────
            {
                'name': 'Aura Pro Wireless Headset',
                'description': (
                    'Studio-grade over-ear wireless headphones with 40 mm custom-tuned drivers, '
                    'active noise cancellation, and 30-hour battery. '
                    'Ultra-plush protein-leather memory-foam ear cups and foldable aluminium arms.'
                ),
                'price': 24999.00,
                'stock': 9,
                'category': 'Audio',
                'image': 'products/headset.png',
            },
            {
                'name': 'Aura Compact Bluetooth Speaker',
                'description': (
                    'Palm-sized 360° speaker with dual passive radiators delivering surprisingly '
                    'deep bass. IPX6 waterproof, 20-hour playtime, USB-C charge, and subtle '
                    'RGB mood ring. Pairs to two devices simultaneously.'
                ),
                'price': 4799.00,
                'stock': 14,
                'category': 'Audio',
                'image': 'products/speaker.png',
            },

            # ── Lighting ───────────────────────────────────────
            {
                'name': 'Aura Minimalist Desk Lamp',
                'description': (
                    'Sculptural warm-to-cool adjustable desk lamp built from solid ash wood and '
                    'brushed aluminium. Touch-dimmer with 5 brightness levels, eye-care flicker-free '
                    'LED (2700 K–6500 K), and a USB-A charging port on the base.'
                ),
                'price': 7299.00,
                'stock': 5,
                'category': 'Lighting',
                'image': 'products/lamp.png',
            },
            {
                'name': 'Aura LED Monitor Backlight',
                'description': (
                    'Bias lighting strip kit for 24–34" monitors. USB-powered RGBIC LEDs with '
                    'music-sync mode, app control, and 16 million colour options. Reduces eye '
                    'strain during long work or gaming sessions.'
                ),
                'price': 1499.00,
                'stock': 40,
                'category': 'Lighting',
                'image': 'products/led_backlight.png',
            },

            # ── Accessories ────────────────────────────────────
            {
                'name': 'Aura Wrist Rest (Keyboard)',
                'description': (
                    'Memory-foam keyboard wrist rest with a premium vegan leather top and '
                    'non-slip silicone base. Perfectly contoured at 18 mm height to reduce '
                    'strain during extended typing sessions. 43 × 8 cm.'
                ),
                'price': 1299.00,
                'stock': 35,
                'category': 'Accessories',
                'image': 'products/wrist_rest.png',
            },
        ]

        for p in products_data:
            product, created = Product.objects.update_or_create(
                name=p['name'],
                defaults={
                    'description': p['description'],
                    'price':       p['price'],
                    'stock':       p['stock'],
                    'category':    p['category'],
                    'image':       p['image'],
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(
                f'[{status}] {product.name} -- INR {product.price:,.2f} ({product.category})'
            ))

        self.stdout.write(self.style.SUCCESS('\nDatabase seeding completed successfully!'))

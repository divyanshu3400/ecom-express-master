from django.core.management.base import BaseCommand
from educart_app.models import Brand, SubBrands

class Command(BaseCommand):
    help = 'Autopopulate brands in the database'
    

    def handle(self, *args, **options):
            # Clear existing categories and subcategories
        SubBrands.objects.all().delete()
        Brand.objects.all().delete()
        
        brands = [
            {
                'brand_name': 'Mobile',
                'brand_type': ['Redmi', 'OPPO', 'Vivo', 'Samsung', 'iPhone', 'Realme', 'Google Pixel']
            },
            {
                'brand_name': 'Clothes',
                'brand_type': ["Levi's", 'Raymond', 'Nike']
            },
        ]

        for brand_data in brands:
            brand_name = brand_data['brand_name']
            brand_type = brand_data['brand_type']

            brand = Brand.objects.create(brand_name=brand_name)

            for type_brand in brand_type:
                SubBrands.objects.create(brand_type=type_brand, brand=brand)

        self.stdout.write(self.style.SUCCESS('Categories and subcategories populated successfully.'))

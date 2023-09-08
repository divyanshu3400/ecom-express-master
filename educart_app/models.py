from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


User = get_user_model()


class OTPToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'otp_token'
        managed = True
        verbose_name = 'OTPToken'
        verbose_name_plural = 'OTPTokens'
        
    def  __str__(self):
       return self.token


class Logo(models.Model):
    image = models.ImageField(upload_to='images/')
    
    class Meta:
        db_table = 'educart_logo'
        managed = True
        verbose_name = 'Logo'
        verbose_name_plural = 'Logos'


class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_confirmation'
        managed = True
        verbose_name = 'EmailConfirmation'
        verbose_name_plural = 'EmailConfirmations'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    # Other fields related to user profile
    profile_image = models.ImageField(upload_to='images/', blank=True, null=True)
    
    class Meta:
        db_table = 'user_profile'
        managed = True
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return self.user.username


class State(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'state_list'
        managed = True
        verbose_name = 'State'
        verbose_name_plural = 'States'
        
    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'cities_list'
        managed = True
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        
    def __str__(self):
        return self.name


class Address(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='addresses', blank=True, null=True)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    class Meta:
        db_table = 'user_address'
        managed = True
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        
    def __str__(self):
        # city_name = self.city.name if self.city else ''
        # state_name = self.state.name if self.state else ''
        return self.address_line_1


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Address)
def associate_address_with_profile(sender, instance, created, **kwargs):
    if created and instance.profile is None:
        profile = Profile.objects.get(user=instance.user)
        instance.profile = profile
        instance.save()


class Category(models.Model):
    cat_name = models.CharField(max_length=100)
    # Other fields specific to categories
    
    class Meta:
        db_table = 'product_category'
        managed = True
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def _str_(self):
        return self.cat_name
    

class Subcategory(models.Model):
    sub_cat_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name='subcategories')
    # Other fields specific to subcategories
    
    class Meta:
        db_table = 'product_sub_category'
        managed = True
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'
        
    def _str_(self):
        return self.sub_cat_name
    

class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    
    class Meta:
        db_table = 'product'
        managed = True
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.title


class Brand(models.Model):
    brand_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    brands_logo = models.ImageField(upload_to='brand_logos/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'products_brand'
        managed = True
        verbose_name = 'ProductBrand'
        verbose_name_plural = 'ProductBrands'

    def __str__(self):
        return self.brand_name


class SubBrands(models.Model):
    brand_type = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.brand_type
    
    class Meta:
        db_table = 'products_sub_brand'
        managed = True
        verbose_name = 'ProductSubBrand'
        verbose_name_plural = 'ProductSubBrands'

        
class MobileProduct(Product):
    size = models.CharField(max_length=20)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    model = models.CharField(max_length=100)
    operating_system = models.CharField(max_length=100)
    storage_capacity = models.CharField(max_length=20)
    ram = models.CharField(max_length=20)
    camera_resolution = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'mobile_product'
        managed = True
        verbose_name = 'MobileProduct'
        verbose_name_plural = 'MobileProducts'



    def __str__(self):
        return f"{self.title} - {self.brand.name} {self.model}"


class ClothSize(models.Model):
    name = models.CharField(max_length=20)
    # Other fields related to size
    
    class Meta:
        db_table = 'cloth_size'
        managed = True
        verbose_name = 'ClothSize'
        verbose_name_plural = 'ClothSizes'
        
    def __str__(self):
        return self.name


class BookProduct(Product):
    author = models.CharField(max_length=100)
    publication_date = models.DateField()
    publisher = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20)
    genre = models.CharField(max_length=100)
    book_class = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    # Other fields specific to book products
    
    class Meta:
        db_table = 'book_product'
        managed = True
        verbose_name = 'BookProduct'
        verbose_name_plural = 'BookProducts'
        
    def __str__(self):
        return f"{self.title} by {self.author}"
    

class ClothingProduct(Product):
    color = models.CharField(max_length=20)
    size = models.ForeignKey(ClothSize, on_delete=models.SET_NULL, null=True)
    material = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    # Other fields specific to clothing products
    
    class Meta:
        db_table = 'clothing_product'
        managed = True
        verbose_name = 'ClothingProduct'
        verbose_name_plural = 'ClothingProducts'
        
    def __str__(self):
        return f"{self.title} - {self.color}, {self.size.name}"


class ProductInventory(models.Model):
    product = models.OneToOneField(ClothingProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'product_inventory'
        managed = True
        verbose_name = 'ProductInventory'
        verbose_name_plural = 'ProductInventorys'
    
    def __str__(self):
        return f"{self.product.title} - Quantity: {self.quantity}"

        
@receiver(post_save, sender=ProductInventory)
def update_product_quantity(sender, instance, **kwargs):
    previous_quantity = instance.product.quantity
    current_quantity = instance.quantity

    if previous_quantity < current_quantity:
        quantity_diff = current_quantity - previous_quantity
        instance.product.quantity += quantity_diff
    elif previous_quantity > current_quantity:
        quantity_diff = previous_quantity - current_quantity
        instance.product.quantity -= quantity_diff

    instance.product.save()


ORDER_STATUS_CHOICES = [('pending', 'Pending'),('processing', 'Processing'),('shipped', 'Shipped'),('delivered', 'Delivered'),('cancelled', 'Cancelled'),]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    ordered_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'user_order'
        managed = True
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.id}"

    def get_product_count(self):
        return self.products.count()

    def get_total_quantity(self):
        order_items = OrderItem.objects.filter(order=self)
        total_quantity = sum(order_item.quantity for order_item in order_items)
        return total_quantity

    def get_ordered_products(self):
        return self.products.all()

    def get_order_total(self):
        return self.total_price
    
    def get_payment_methods(self):
        return self.payments.values_list('payment_method', flat=True)

    def is_fully_paid(self):
        total_paid = self.payments.aggregate(total_paid=models.Sum('amount')).get('total_paid', 0)
        return total_paid >= self.total_price

    def can_be_cancelled(self):
        # Logic to determine if the order can be cancelled
        pass

    def update_status(self, new_status):
        if new_status not in [choice[0] for choice in ORDER_STATUS_CHOICES]:
            raise ValueError("Invalid status value")
        self.status = new_status
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_item'
        managed = True
        verbose_name = 'OrderItem'
        verbose_name_plural = 'OrderItems'
        
    def __str__(self):
        return f"Order #{self.order.id} - {self.product.title}"
    

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'user_payment'
        managed = True
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"Payment #{self.id} for Order #{self.order.id}"


class Feedback(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    
    def get_star_rating(self):
        full_stars = int(self.rating)
        half_stars = 1 if (self.rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_stars

        return {
            'full_stars': full_stars,
            'half_stars': half_stars,
            'empty_stars': empty_stars}

    def __str__(self):
        return f"Rating: {self.rating} - Product: {self.product.name}"
    
    class Meta:
        db_table = 'user_feedback'
        managed = True
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        return f"Product: {self.product.name} - User: {self.user.username}"
from django.contrib import admin
from .models import Logo,Profile, Brand,SubBrands,Category,State,City,ClothingProduct,Product,Subcategory,Order,Payment
from .models import Address,MobileProduct,ClothSize,BookProduct,ProductInventory,OrderItem,Feedback
# Register your models here.


class LogoAdmin(admin.ModelAdmin):
    list_display=['image']
    
admin.site.register(Logo,LogoAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display=['phone_number']

admin.site.register(Profile,ProfileAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display=['brand_name','description','brands_logo','created_at','updated_at']

admin.site.register(Brand,BrandAdmin)

class SubBrandsAdmin(admin.ModelAdmin):
    list_display=['brand_type']

admin.site.register(SubBrands,SubBrandsAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display = ['address_line_1','address_line_2','state','city','postal_code','country','latitude','longitude']

admin.site.register(Address,AddressAdmin)


class MobileProductAdmin(admin.ModelAdmin):
    list_display = ['size','brand','model','operating_system','storage_capacity','ram','camera_resolution']
    
admin.site.register(MobileProduct, MobileProductAdmin)
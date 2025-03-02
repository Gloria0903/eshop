'''admin.py file'''
from django.contrib import admin
from .models import Product, Customer, Order, Category, ProductSizeColor, Size, Color

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductSizeColor)
admin.site.register(Size)
admin.site.register(Color)

'''admin.py file'''
from django.contrib import admin
from .models import Products, Customer, Order, Category


@admin.register(Products)
class ProductsModelAdmin(admin.ModelAdmin):
    '''products'''
    list_display = ['id', 'title', 'discounted_price', 'category', 'product_image']


admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Category)

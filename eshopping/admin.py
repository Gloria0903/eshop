from django.contrib import admin
from .models import Products


@admin.register(Products)
class ProductsModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'discounted_price', 'category', 'product_image']

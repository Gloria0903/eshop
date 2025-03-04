''''form.py'''
from .models import Product, Category, Size, Color
from django.contrib.auth.forms import UserCreationForm
from django import forms
# from django.http import request

from .models import Customer


class CustomerRegistrationForm(UserCreationForm):
    '''form for customer'''
    class Meta:
        '''meta'''
        model = Customer
        fields = ['first_name','last_name', 'email', 'password1', 'password2']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
        }


class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Size Name'}),
        }


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Color Name'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'selling_price', 'discounted_price',
                  'description', 'product_image', 'categories', 'sizes', 'colors']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Title'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Selling Price'}),
            'discounted_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Discounted Price'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Product Description'}),
            'product_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'sizes': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'colors': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

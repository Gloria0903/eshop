''''form.py'''
from django.contrib.auth.forms import UserCreationForm
from django import forms
# from django.http import request

from .models import Customer


class CustomerRegistrationForm(UserCreationForm):
    '''form for customer'''
    class Meta:
        '''meta'''
        model = Customer
        fields = ['first_name', 'username','last_name', 'email', 'phone', 'password1', 'password2']

    # You can customize the widgets or add additional validations if needed
    widgets = {
        'first_name': forms.TextInput(attrs={'autofocus': 'True', 'class': 'form-control'}),
        'last_name': forms.TextInput(attrs={'autofocus': 'True', 'class': 'form-control'}),
        'username': forms.TextInput(attrs={'autofocus': 'True', 'class': 'form-control'}),
        'email': forms.EmailInput(attrs={'class': 'form-control'}),
        'phone': forms.TextInput(attrs={'class': 'form-control'}),
        'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
        'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
    }

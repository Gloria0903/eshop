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
        fields = ['first_name','last_name', 'email', 'password1', 'password2']
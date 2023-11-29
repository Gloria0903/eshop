''''form.py'''
from django.contrib.auth.forms import UserCreationForm
from django import forms
# from django.http import request

# from .models import Products


class CustomerRegistrationForm(UserCreationForm):
    '''form for customer'''
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'autofocus': 'True', 'class': 'form-control'
        }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'autofocus': 'True', 'class': 'form-control'
        }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'autofocus': 'True', 'class': 'form-control'
        }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        }))
    password2 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        }))

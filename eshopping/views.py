from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .forms import CustomerRegistrationForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'index.html')


def shop(request):
    return render(request, 'shop.html')


def detail(request):
    return render(request, 'detail.html')


def contact(request):
    return render(request, 'contact.html')


def checkout(request):
    return render(request, 'checkout.html')


def cart(request):
    return render(request, 'cart.html')


def get(request, val):
    return render(request, 'category.html', locals())


class CategoryView(View):
    pass


# def get(request):
#     form = CustomerRegistrationForm()
#     return render(request, 'customerregistration.html', locals())
#
#
# class CustomerRegistrationView(View):
#     pass


def customerregistration(request):
    username = request.POST.get['username']
    password = request.POST.get['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        # the password was correct. Do whatever you want to do next.
        pass
    else:
        # the password was incorrect. Return an error message or take some other action.
        pass


def customerregistration(request):
    username = request.POST.get['username']
    password = request.POST.get['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # the user is now logged in. Do whatever you want to do next.
        pass
    else:
        # the password was incorrect. Return an error message or take some other action.
        pass



@login_required
def my_view(request):
    # this view will only be accessible to logged-in users.
    pass


def logout_view(request):
    logout(request)
    # the user is now logged out. Do whatever you want to do next.
    pass
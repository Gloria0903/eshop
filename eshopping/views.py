from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from .models import Products, Customer
from django.contrib.auth.models import User


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


def customerregistration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer = Customer(user=user, name=request.POST['name'], email=request.POST['email'])
            customer.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'customerregistration.html', {'form': form})


def customerlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    else:
        return render(request, 'customerlogin.html')


# Read
def index(request):
    data = Products.objects.all()
    return render(request,'index.html',{'data': data})


# create
def insertData(request):
    if request.method == 'POST':
        productname=request.POST.get('productname')
        title =request.POST.get('title')
        selling_price=request.POST.get('selling_price')
        discounted_price=request.POST.get('discounted_price')
        description=request.POST.get('description')
        composition=request.POST.get('composition')
        category=request.POST.get('category')
        product_image=request.POST.get('product_image')
        hifadhi = Products(productname=productname,title=title,selling_price=selling_price,discounted_price=discounted_price,description=description,composition=composition,category=category,product_image=product_image)

        hifadhi.save()
        return redirect('/')
    else:
        return render(request,'index.html')

        # Update
def updateData(request,id):
    if request.method=='POST':
        productname = request.POST.get('productname')
        title = request.POST.get('title')
        selling_price = request.POST.get('selling_price')
        discounted_price = request.POST.get('discounted_price')
        description = request.POST.get('description')
        composition = request.POST.get('composition')
        category = request.POST.get('category')
        product_image = request.POST.get('product_image')

        rekebisha = Products.objects.get(id=id)
        rekebisha.productname=productname
        rekebisha.title=title
        rekebisha.selling_price=selling_price
        rekebisha.discounted_price=discounted_price
        rekebisha.description=description
        rekebisha.composition=composition
        rekebisha.category=category
        rekebisha.product_image=product_image
        rekebisha.save()
        return redirect('/')
    else:
        p=Products.objects.get(id=id)
        return render(request,'category.html',{'p':p})

        # delete
def delete(request,id):
     p=Products.objects.get(id=id)
     p.delete()
     return redirect('/')


        # customer logic


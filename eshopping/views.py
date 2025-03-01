'''views.py file'''
from django.contrib import messages
from django.contrib.auth.hashers import check_password,make_password
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import path
from django.views import View
from django_daraja.mpesa.core import MpesaClient
from eshopping.forms import CustomerRegistrationForm
from .models import Products, Customer, Category,Order
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import CustomerRegistrationForm # or however you are handling your form
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Cart

# Register
class CustomerRegistration(View):
    template_name = "customerregistration.html"

    def get(self, request):
        '''loads register html file'''
        return render(request, 'customerregistration.html')

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect("index")
        import json
        errors = json.loads(form.errors.as_json())
        for msg in errors:
            messages.error(request, f"{msg}: {errors[msg][0]['message']}")
        return render(request, self.template_name, {'form': form})

# Login
class CustomerLogin(View):
    '''customer login'''
    def get(self, request):
        '''loads html'''
        user = request.user
        return_url = request.GET.get('next')
        if user.is_authenticated:
            if return_url is not None:
                return HttpResponseRedirect(return_url)
            return redirect('index')
        return render(request, 'customerlogin.html', {'return_url': return_url})

    def post(self, request):
        '''customer login'''
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully')
            return_url = request.POST.get('return_url')
            print("return_url: ", return_url)
            if return_url is not None:
                return HttpResponseRedirect(return_url)
            return redirect('index')
        else:
            error_message = 'Email or Password is invalid'
            messages.error(request, error_message)
        return render(request, 'customerlogin.html', {'error': error_message})


# Logout
def customer_logout(request):
    '''logouts customer out the system'''
    request.session.clear()
    return redirect('customerlogin')


@login_required(login_url='customerlogin')
def index(request):
    '''load index.html'''
    #pylint: disable = E1101:no-member
    products = Products.objects.all()
    print("logged in user: ", request.user.is_authenticated)
    for product in products:
        print(f"Product ID: {product.id}")
    return render(request, 'index.html',{'products': products})


def shop(request):
    '''load shop.html'''
    #pylint: disable = E1101:no-member
    products = Products.objects.all()
    return render(request, 'shop.html',{'products': products})

# @login_required(login_url='customerlogin')
def detail(request, id):
    '''load detail.html'''
    product = get_object_or_404(Products, id=id)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity'))
        user_id = 1
        user = get_object_or_404(Customer, id=user_id)
        Cart.objects.create(user=user, product=product, quantity=qty)
        return redirect('cart')
    return render(request, 'detail.html', {'product': product})


def contact(request):
    '''load contact.html'''
    return render(request, 'contact.html')


def checkout(request):
    '''load checkout.html'''
    return render(request, 'checkout.html')


@login_required(login_url='customerlogin')
def cart(request):
    '''load cart.html'''
    cartItems = Cart.objects.filter(user_id=1)
    subtotals = 0
    for item in cartItems:
        subtotals += item.total_price()
    return render(request, 'cart.html', {'cartItems': cartItems, 'subtotals': subtotals})

def delete_cart_item(request, cart_id):
    '''delete cart item'''
    cartItem = get_object_or_404(Cart, id=cart_id)
    cartItem.delete()
    return redirect('cart')

def update_cart_qty(request, cart_id):
    '''update cart item'''
    if request.method == 'GET':
        cartItem = get_object_or_404(Cart, id=cart_id)
        qty = int(request.GET.get('quantity'))
        if (qty > 0):
            cartItem.quantity = qty
            cartItem.save()
            messages.success(request, 'Cart updated successfully')
        else:
            cartItem.delete()
        return redirect('cart')
    
    return redirect('cart')
# pylint: disable = W0613
def get(request, val):
    '''load category.html'''
    return render(request, 'category.html', locals())


class CategoryView(View):
    '''load northing yet'''
    #pylint: disable = W0107
    pass


# create
def insert_data(request):
    '''add data to db'''
    if request.method == 'POST':
        product_name = request.POST.get('productname')
        title = request.POST.get('title')
        selling_price = request.POST.get('selling_price')
        discounted_price = request.POST.get('discounted_price')
        description = request.POST.get('description')
        composition = request.POST.get('composition')
        category = request.POST.get('category')
        product_image = request.POST.get('product_image')
        create_product = Products(productname=product_name, title=title,
                        selling_price=selling_price,
                        discounted_price=discounted_price, description=description,
                        composition=composition,
                        category=category, product_image=product_image)

        create_product.save()
        return redirect('/')
    else:
        return render(request, 'index.html')



# pylint: disable = W0613
def delete(request, id):
    '''load delete product'''
    #pylint: disable= E1101
    p = Products.objects.get(id=id)
    p.delete()
    return redirect('/')


# Create your views here.
class Index(View):
    '''handles index'''
    def post(self, request):
        '''posting'''
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        #pylint: disable = W0621:redefined-outer-name
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity - 1
                else:
                    cart[product] = quantity + 1

            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        print('cart', request.session['cart'])
        return redirect('homepage')

    def get(self, request):
        '''gets cart'''
        print("logged in user: ", request.user)
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')


def store(request):
    '''handles store'''
    #pylint: disable = W0621
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    products = None
    categories = Category.get_all_categories()
    category_id = request.GET.get('category')
    if category_id:
        products = Products.get_all_products_by_category_id(category_id)
    else:
        products = Products.get_all_products()

    data = {}
    data['products'] = products
    data['categories'] = categories

    print('you are : ', request.session.get('email'))
    return render(request, 'index.html', data)



class CheckOut(View):
    '''checkout for customer'''
    def post(self, request):
        '''post a checkout'''
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        # pylint: disable = W0621
        cart = request.session.get('cart')
        #pylint: disable = E1101
        products = Products.get_products_by_id(list(cart.keys()))
        print(address, phone, customer, cart, products)

        for product in products:
            print(cart.get(str(product.id)))
            order = Order(customer=Customer(id=customer),
                        product=product,
                        price=product.price,
                        address=address,
                        phone=phone,
                        quantity=cart.get(str(product.id)))
            order.save()
        request.session['cart'] = {}

        return redirect('cart')


# orders view


class OrderView(View):
    '''handles orders'''

    def get(self, request):
        '''gets Order'''
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(orders)
        return render(request, 'orders.html', {'orders': orders})

def payment(request):
    """
    Handles Mpesa payment.
    e.g http://127.0.0.1:8000/payment/?phone=07########&amount=1&reference=ref123&description=test
    """
    cl = MpesaClient()

    # Get credentials from the request (GET or POST depending on your use case)
    phone_number = request.GET.get('phone')
    amount_string = request.GET.get('amount')
    account_reference = request.GET.get('reference')
    transaction_desc = request.GET.get('description')
    callback_url = 'https://darajambili.herokuapp.com/express-payment'

    # Validate inputs
    if not all([phone_number, amount_string, account_reference, transaction_desc]):
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    try:
        # Convert amount to integer
        amount = int(amount_string)
    except ValueError:
        return JsonResponse({"error": "Invalid amount. Must be a numeric value."}, status=400)

    # Proceed with Mpesa STK push
    try:
        response = cl.stk_push(
            phone_number, amount,
            account_reference, transaction_desc,
            callback_url)

        return HttpResponse(response)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_view')

from django.shortcuts import render
from .models import Cart

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

from django.http import JsonResponse

@login_required
def update_cart(request, product_id, quantity):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.quantity = quantity
    cart_item.save()
    total_price = sum(item.total_price() for item in Cart.objects.filter(user=request.user))
    return JsonResponse({'total_price': total_price})

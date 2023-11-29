'''views.py file'''
from django.contrib import messages
from django.contrib.auth.hashers import check_password,make_password
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from eshopping.forms import CustomerRegistrationForm
from .models import Products, Customer, Category,Order
# from django.contrib.auth.models import User


def index(request):
    '''load index.html'''
    return render(request, 'index.html')


def shop(request):
    '''load shop.html'''
    return render(request, 'shop.html')


def detail(request):
    '''load detail.html'''
    return render(request, 'detail.html')


def contact(request):
    '''load contact.html'''
    return render(request, 'contact.html')


def checkout(request):
    '''load checkout.html'''
    return render(request, 'checkout.html')


def cart(request):
    '''load cart.html'''
    return render(request, 'cart.html')

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

        # Update

# pylint: disable = W0622
def update_data(request, id):
    '''update the data in db'''
    if request.method == 'POST':
        productname = request.POST.get('productname')
        title = request.POST.get('title')
        selling_price = request.POST.get('selling_price')
        discounted_price = request.POST.get('discounted_price')
        description = request.POST.get('description')
        composition = request.POST.get('composition')
        category = request.POST.get('category')
        product_image = request.POST.get('product_image')

        #pylint: disable = E1101
        product = Products.objects.get(id=id)
        product.productname = productname
        product.title = title
        product.selling_price = selling_price
        product.discounted_price = discounted_price
        product.description = description
        product.composition = composition
        product.category = category
        product.product_image = product_image
        product.save()
        return redirect('/')
    else:
        #pylint: disable = E1101
        p = Products.objects.get(id=id)
        return render(request, 'category.html', {'p': p})

        # delete

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
        # print()
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


# login/logout view


class CustomerLogin(View):
    '''customer login'''
    return_url = None

    def get(self, request):
        '''loads html'''
        CustomerLogin.return_url = request.GET.get('return_url')
        return render(request, 'customerlogin.html')

    def post(self, request):
        '''customer login'''
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id
                if CustomerLogin.return_url:
                    return HttpResponseRedirect(CustomerLogin.return_url)
                else:
                    CustomerLogin.return_url = None
                    return redirect('index')
            else:
                error_message = 'Invalid password'
        else:
            error_message = 'Invalid email'

        if customer:
            # Check if customer is not None before accessing attributes
            print("Email:", customer.email)
        else:
            print("Customer not found for email:", email)

        return render(request, 'customerlogin.html', {'error': error_message})



def customer_logout(request):
    '''logouts customer out the system'''
    request.session.clear()
    return redirect('login')


# signup view
class CustomerRegistration(View):
    '''register customer'''
    def get(self, request):
        '''loads register html file'''
        return render(request, 'customerregistration.html')

    def post(self, request):
        '''create customer'''
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Process valid form data
            customer = form.save(commit=False)
            customer.password = make_password(form.cleaned_data['password1'])
            # Process valid form data
            customer.register()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('index')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
            # Form is invalid, pass form to template for error display
            return render(request, 'customerregistration.html', {'form': form})




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

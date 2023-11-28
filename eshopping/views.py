from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from .models import Products, Customer, Category
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
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    else:
        return render(request, 'customerlogin.html')


# Read
def index(request):
    data = Products.objects.all()
    return render(request, 'index.html', {'data': data})


# create
def insertData(request):
    if request.method == 'POST':
        productname = request.POST.get('productname')
        title = request.POST.get('title')
        selling_price = request.POST.get('selling_price')
        discounted_price = request.POST.get('discounted_price')
        description = request.POST.get('description')
        composition = request.POST.get('composition')
        category = request.POST.get('category')
        product_image = request.POST.get('product_image')
        hifadhi = Products(productname=productname, title=title, selling_price=selling_price,
                           discounted_price=discounted_price, description=description, composition=composition,
                           category=category, product_image=product_image)

        hifadhi.save()
        return redirect('/')
    else:
        return render(request, 'index.html')

        # Update


def updateData(request, id):
    if request.method == 'POST':
        productname = request.POST.get('productname')
        title = request.POST.get('title')
        selling_price = request.POST.get('selling_price')
        discounted_price = request.POST.get('discounted_price')
        description = request.POST.get('description')
        composition = request.POST.get('composition')
        category = request.POST.get('category')
        product_image = request.POST.get('product_image')

        rekebisha = Products.objects.get(id=id)
        rekebisha.productname = productname
        rekebisha.title = title
        rekebisha.selling_price = selling_price
        rekebisha.discounted_price = discounted_price
        rekebisha.description = description
        rekebisha.composition = composition
        rekebisha.category = category
        rekebisha.product_image = product_image
        rekebisha.save()
        return redirect('/')
    else:
        p = Products.objects.get(id=id)
        return render(request, 'category.html', {'p': p})

        # delete


def delete(request, id):
    p = Products.objects.get(id=id)
    p.delete()
    return redirect('/')





# Create your views here.
class Index(View):

    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
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
        # print()
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')


def store(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    products = None
    categories = Category.get_all_categories()
    categoryID = request.GET.get('category')
    if categoryID:
        products = Products.get_all_products_by_categoryid(categoryID)
    else:
        products = Products.get_all_products()

    data = {}
    data['products'] = products
    data['categories'] = categories

    print('you are : ', request.session.get('email'))
    return render(request, 'index.html', data)


# login/logout view
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.hashers import check_password, make_password
# from store.models.customer import Customer
from django.views import View


class CustomerLogin(View):
    return_url = None

    def get(self, request):
        customerlogin.return_url = request.GET.get('return_url')
        return render(request, 'customerlogin.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id

                if customerlogin.return_url:
                    return HttpResponseRedirect(customerlogin.return_url)
                else:
                    customerlogin.return_url = None
                    return redirect('homepage')
            else:
                error_message = 'Invalid !!'
        else:
            error_message = 'Invalid !!'

        print(email, password)
        return render(request, 'customerlogin.html', {'error': error_message})


def customerlogout(request):
    request.session.clear()
    return redirect('login')


# signup view
class CustomerRegistration(View):
    def get(self, request):
        return render(request, 'customerregistration.html')

    def post(self, request):
        postData = request.POST
        first_name = postData.get('firstname')
        last_name = postData.get('lastname')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        # validation
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }
        error_message = None

        customer = Customer(first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                            email=email,
                            password=password)
        error_message = self.validateCustomer(customer)

        if not error_message:
            print(first_name, last_name, phone, email, password)
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('homepage')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render(request, 'customerregistration.html', data)

    def validateCustomer(self, customer):
        error_message = None
        if (not customer.first_name):
            error_message = "Please Enter your First Name !!"
        elif len(customer.first_name) < 3:
            error_message = 'First Name must be 3 char long or more'
        elif not customer.last_name:
            error_message = 'Please Enter your Last Name'
        elif len(customer.last_name) < 3:
            error_message = 'Last Name must be 3 char long or more'
        elif not customer.phone:
            error_message = 'Enter your Phone Number'
        elif len(customer.phone) < 10:
            error_message = 'Phone Number must be 10 char Long'
        elif len(customer.password) < 5:
            error_message = 'Password must be 5 char long'
        elif len(customer.email) < 5:
            error_message = 'Email must be 5 char long'
        elif customer.isExists():
            error_message = 'Email Address Already Registered..'
        # saving

        return error_message




class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
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
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
# from store.models.customer import Customer
from django.views import View


class OrderView(View):

    def get(self, request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(orders)
        return render(request, 'orders.html', {'orders': orders})

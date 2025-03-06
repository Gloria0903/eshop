'''views.py file'''
from .forms import ProductForm, CategoryForm, SizeForm, ColorForm, CustomerRegistrationForm
from .models import Product, Category, Size, Color, Payment, OrderItem, Cart, ProductSizeColor, Customer, Category, Order
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django_daraja.mpesa.core import MpesaClient
from eshopping.forms import CustomerRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_daraja.mpesa.utils import api_base_url, mpesa_config, mpesa_access_token
import requests
from datetime import datetime
import base64
import time

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
            return_url = request.POST.get('return_url', None)
            if return_url and return_url != 'None':
                print("Redirecting to next: ", return_url)
                return HttpResponseRedirect(return_url)
            else: 
                if user.is_superuser:
                    print("Redirecting to admin")
                    return redirect('admin_dashboard')
                else: 
                    print("Redirecting to home")
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

def index(request):
    '''load index.html'''
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'index.html',{'products': products, 'categories': categories})


def shop(request):
    '''load shop.html'''
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'shop.html',{'products': products, 'categories': categories})

def detail(request, id):
    '''load detail.html'''
    product = get_object_or_404(Product, id=id)
    products = Product.objects.all().order_by('-id')[:10]
    categories = Category.objects.all()
    if request.method == 'POST':
        qty = int(request.POST.get('quantity'))
        user_id = 1
        user = get_object_or_404(Customer, id=user_id)
        Cart.objects.create(user=user, product=product, quantity=qty)
        return redirect('cart')
    return render(request, 'detail.html', {'product': product, 'similar_products': products, 'categories': categories})


def contact(request):
    '''load contact.html'''
    categories = Category.objects.all()
    return render(request, 'contact.html', {'categories': categories})


@login_required(login_url='customerlogin')
def checkout(request):
    '''load checkout.html'''
    user = request.user
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    categories = Category.objects.all()
    return render(request, 'checkout.html', {'categories': categories, 'cartItems': cart_items, 'total_price': total_price, "customer": user})


@login_required(login_url='customerlogin')
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    categories = Category.objects.all()
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cartItems': cart_items, 'subtotals': total_price, 'categories': categories})


@login_required(login_url='customerlogin')
def add_to_cart(request, product_id):
    print("Adding to cart")
    product = get_object_or_404(Product, id=product_id)
    product_size_color = None
    quantity = int(request.POST.get('quantity', 1))
    size_id = request.POST.get('size', None)
    color_id = request.POST.get('color', None)
    colorVariation = None
    sizeVariation = None

    if size_id and color_id:
        color = get_object_or_404(Color, id=color_id)
        size = get_object_or_404(Size, id=size_id)
        colorVariation = color.name
        sizeVariation = size.name
        size_id = int(size_id)
        color_id = int(color_id)
        product_size_color = get_object_or_404(
            ProductSizeColor, product=product, size_id=size_id)
    elif size_id:
        size_id = int(size_id)
        size = get_object_or_404(Size, id=size_id)
        sizeVariation = size.name
        product_size_color = get_object_or_404(
            ProductSizeColor, product=product, size_id=size_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        product_size_color=product_size_color,
        defaults={'quantity': quantity},
        colorVariation=colorVariation,
        sizeVariation=sizeVariation
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    messages.success(request, 'Item added to cart successfully')
    return redirect('cart_view')


@login_required(login_url='customerlogin')
def update_cart_quantity(request, cart_id, action):
    cart_item = get_object_or_404(Cart, id=cart_id)
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    messages.success(request, 'Cart updated successfully')
    return redirect('cart_view')


@login_required(login_url='customerlogin')
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart successfully')
    return redirect('cart_view')


@login_required(login_url='customerlogin')
def create_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('cart_view')
    
    full_name = request.POST.get('first_name', '') + ' ' + request.POST.get('last_name', '')
    city = request.POST.get('city', '')
    address = full_name + ', ' + city
    phone = request.POST.get('phone', '')
    total_price = sum(item.total_price() for item in cart_items)

    order = Order.objects.create(
        customer=request.user,
        totalAmount=total_price,
        address=address,
        phone=phone
    )

    for cart_item in cart_items:
        product_size_color = cart_item.product_size_color
        color = product_size_color.color if product_size_color else None
        size = product_size_color.size if product_size_color else None

        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            color=color,
            size=size,
            quantity=cart_item.quantity,
            price=cart_item.total_price()
        )
        
    cart_items.delete()
    messages.success(request, 'Order placed successfully')
    return redirect('pay_order', order_id=order.id)


@login_required(login_url='customerlogin')
def pay_order(request, order_id):
    """
    Handles Mpesa payment.
    """
    order = Order.objects.get(id=order_id)
    amount = int(order.totalAmount)
    if request.method == 'POST':
        phone = request.POST.get('phone')
        account_reference = 'Chic Wear'
        transaction_desc = 'Payment for order'
        callback_url = f"https://qtc6a7740fe1c845c0396f6ba7b9.free.beeceptor.com/orders/{order_id}/payment-confirmation"
        cl = MpesaClient()
        try:
            response = cl.stk_push(
                phone, amount,
                account_reference, transaction_desc,
                callback_url)
            response_data = response.json()
            checkout_request_id = response_data.get('CheckoutRequestID')
            existing_payment = Payment.objects.filter(order=order)
            if existing_payment.exists():
                existing_payment.delete()
            Payment.objects.create(
                order=order, transactionId=checkout_request_id, amountPaid=amount, referencePhoneNumber=phone)
            time.sleep(10)
            return redirect('transaction_status', transaction_id=checkout_request_id)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    return render(request, 'pay_order.html', {'order': order})


@login_required(login_url='customerlogin')
def query_transaction_status(request, transaction_id):
    """
    Queries the status of an Mpesa transaction.
    """
    payment = get_object_or_404(Payment, transactionId=transaction_id)

    url = api_base_url() + 'mpesa/stkpushquery/v1/query'
    order = payment.order
    mpesa_environment = mpesa_config('MPESA_ENVIRONMENT')
    if mpesa_environment == 'sandbox':
        business_short_code = mpesa_config('MPESA_EXPRESS_SHORTCODE')
    else:
        business_short_code = mpesa_config('MPESA_SHORTCODE')
    passkey = mpesa_config('MPESA_PASSKEY')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((business_short_code + passkey + timestamp).encode('ascii')).decode('utf-8') 
    
    data = {
        'BusinessShortCode': business_short_code,
        'Password': password,
        'Timestamp': timestamp,
        'CheckoutRequestID': transaction_id,
    }
    
    headers = {
        'Authorization': 'Bearer ' + mpesa_access_token(),
        'Content-type': 'application/json'
    }
    
    try:
        r = requests.post(url, json=data, headers=headers)
        response = r.json()

        result = {}

        resultCode = response.get('ResultCode', '')
        errorCode = response.get('errorCode', None)
        if resultCode == '0':
            payment.status = 'COMPLETED'
            order.isPaid = True
            order.save()
            result['success'] = True
            result['message'] = 'Payment Completed'
            result['description'] = "Your payment has been processed successfully. Thank you for shopping with us!"
        elif errorCode is not None:
            # The request is being redirected, wait and try again
            time.sleep(5)
            return query_transaction_status(request, transaction_id)
        else:
            result['success'] = False
            result['message'] = 'Payment Failed'
            result['description'] = response.get('ResultDesc', '')
            payment.status = 'FAILED'
            payment.resultCode = resultCode
            payment.resultDesc = response.get('ResultDesc', '')
        payment.save()
        
        return render(request, 'confirm_payment.html', {'response': result, 'order_id': payment.order.id})
    except Exception as e:
        messages.error(request, "An error occurred while processing your payment")
        return render(request, 'confirm_payment.html', {'order_id': payment.order.id})


@api_view(['GET', 'POST'])
def mpesa_callback(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        order = Order.objects.get(id=order_id)
        payment = get_object_or_404(Payment, order=order)
        if data['Body']['stkCallback']['ResultCode'] == 0:
            callbackMetaData = data['Body']['stkCallback'].get(
            'CallbackMetadata', None)

            if callbackMetaData is not None:
                data = data['Body']['stkCallback']['CallbackMetadata']['Item']
                amount = data[0].get('Value')
                receipt_number = data[1].get('Value')
                transaction_date = data[3].get('Value')
                phone_number = data[4].get('Value')


                payment.amountPaid = amount
                payment.receiptNumber = receipt_number
                payment.transactionDate = transaction_date
                payment.referencePhoneNumber = phone_number
                payment.responseReceived = True
                payment.status = 'COMPLETED'
                payment.save()

                order.isPaid = True
                order.save()

                return Response({"message": "Your transaction has been processed successfully!"}, status=201)

                # return render(request, 'confirm_payment.html', {'success': True, 'description': f"Your payment for order #{order_id} been processed successfully. Thankyou for shopping with us!", "order_id": order_id})
        else:
            resultCode = data['Body']['stkCallback']['ResultCode']
            resultDesc = data['Body']['stkCallback']['ResultDesc']
            payment.resultCode = resultCode
            payment.resultDesc = resultDesc
            payment.responseReceived = True
            payment.status = 'FAILED'
            payment.save()
            return Response({"message": "Your transaction could not be completed."}, status=400)
            # return render(request, 'confirm_payment.html', {"success": False, "description": resultCode, "order_id": order_id})
    return Response({'message': 'Method not allowed'}, status=405)

# admin
@admin_required
def admin_dashboard(request):
    '''load admin dashboard'''
    total_products = Product.objects.all().count()
    total_categories = Category.objects.all().count()
    total_orders = Order.objects.all().count()
    total_customers = Customer.objects.all().count()
    return render(request, 'admin/stats.html', {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'total_customers': total_customers
    })

@admin_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a category list view
            return redirect('admin_categories')
    else:
        form = CategoryForm()
        categories = Category.objects.all()
    return render(request, 'admin/categories.html', {'form': form, 'categories': categories})


@admin_required
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('admin_categories')
        else:
            messages.error(request, 'Category update failed')
            return render(request, 'admin/categories.html', {'form': form, 'categories': categories, 'type': 'edit'})
    else:
        form = CategoryForm(instance=category)
        return render(request, 'admin/categories.html', {'form': form, 'categories': categories, 'type': 'edit'})


@admin_required
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    categories = Category.objects.all()
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully')
        return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
        return render(request, 'admin/categories.html', {'form': form, 'categories': categories, 'category': category, 'type': 'delete'})


@admin_required
def create_size(request):
    if request.method == 'POST':
        form = SizeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('size_listing')
    else:
        form = SizeForm()
        sizes = Size.objects.all()
    return render(request, 'admin/sizes.html', {'form': form, 'sizes': sizes})


@admin_required
def edit_size(request, id):
    size = get_object_or_404(Size, id=id)
    sizes = Size.objects.all()
    if request.method == 'POST':
        form = SizeForm(request.POST, instance=size)
        if form.is_valid():
            form.save()
            messages.success(request, 'Size updated successfully')
            return redirect('size_listing')
        else:
            messages.error(request, 'Size update failed')
            return render(request, 'admin/sizes.html', {'form': form, 'sizes': sizes, 'type': 'edit'})
    else:
        form = SizeForm(instance=size)
        return render(request, 'admin/sizes.html', {'form': form, 'sizes': sizes, 'type': 'edit'})


@admin_required
def delete_size(request, id):
    size = get_object_or_404(Size, id=id)
    sizes = Size.objects.all()
    if request.method == 'POST':
        size.delete()
        messages.success(request, 'Size deleted successfully')
        return redirect('size_listing')
    else:
        form = SizeForm(instance=size)
        return render(request, 'admin/sizes.html', {'form': form, 'sizes': sizes, 'size': size, 'type': 'delete'})


@admin_required
def create_color(request):
    if request.method == 'POST':
        form = ColorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('color_listing')
    else:
        form = ColorForm()
        colors = Color.objects.all()
    return render(request, 'admin/colors.html', {'form': form, 'colors': colors})


@admin_required
def edit_color(request, id):
    color = get_object_or_404(Color, id=id)
    colors = Color.objects.all()
    if request.method == 'POST':
        form = ColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            messages.success(request, 'Color updated successfully')
            return redirect('color_listing')
        else:
            messages.error(request, 'Color update failed')
            return render(request, 'admin/colors.html', {'form': form, 'colors': colors, 'type': 'edit'})
    else:
        form = ColorForm(instance=color)
        return render(request, 'admin/colors.html', {'form': form, 'colors': colors, 'type': 'edit'})


@admin_required
def delete_color(request, id):
    color = get_object_or_404(Color, id=id)
    colors = Color.objects.all()
    if request.method == 'POST':
        color.delete()
        messages.success(request, 'Color deleted successfully')
        return redirect('color_listing')
    else:
        form = ColorForm(instance=color)
        return render(request, 'admin/colors.html', {'form': form, 'colors': colors, 'color': color, 'type': 'delete'})

@admin_required
def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product_form.save()
            messages.success(request, 'Product created successfully')
        return redirect('admin_products')
    else:
        product_form = ProductForm()

    return render(request, 'admin/product_form.html', {
        'form': product_form,
    })


@admin_required
def list_admin_products(request):
    products = Product.objects.all().order_by('-id')
    products_count = products.count()
    return render(request, 'admin/products.html', {'products': products, 'products_count': products_count})

@admin_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully')
            return redirect('admin_products')
        else:
            messages.error(request, 'Product update failed')
            return render(request, 'admin/product_form.html', {'form': form, 'type': 'edit'})
    else:
        form = ProductForm(instance=product)
        return render(request, 'admin/product_form.html', {'form': form, 'type': 'edit'})

@admin_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully')
        return redirect('admin_products')
    else:
        return render(request, 'admin/product_form.html', {'product': product, 'type': 'delete'})
    

@admin_required
def admin_list_orders(request):
    orders = Order.objects.all().order_by('-id')
    order_count = orders.count()
    return render(request, 'admin/orders.html', {'orders': orders, 'order_count': order_count})


@login_required(login_url='customerlogin')
def get_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/order_details.html', {'order': order})

@admin_required
def get_customers(request):
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'admin/customers.html', {'customers': customers})


@admin_required
def get_customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, 'admin/customer_detail.html', {'customer': customer})
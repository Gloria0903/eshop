'''views.py file'''
from .forms import ProductForm, CategoryForm, SizeForm, ColorForm
from .models import Product, Category, Size, Color
from django.contrib import messages
from django.contrib.auth.hashers import check_password,make_password
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import path
from django.views import View
from django_daraja.mpesa.core import MpesaClient
from eshopping.forms import CustomerRegistrationForm
from .models import Product, Customer, Category,Order
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import CustomerRegistrationForm # or however you are handling your form
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from .models import Product, Cart, ProductSizeColor

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
    product_size_colors = ProductSizeColor.objects.filter(product=product)
    for p in product_size_colors:
        print("Product size color: ", p.__dict__)
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

    for cart_item in cart_items:
        Order.objects.create(
            product_size_color=cart_item.product_size_color,
            customer=request.user,
            quantity=cart_item.quantity,
            price=cart_item.total_price(),
            address=address,
            phone=phone
        )
    cart_items.delete()
    messages.success(request, 'Order placed successfully')
    return redirect('order_history')


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


# admin
@admin_required
def admin_dashboard(request):
    '''load admin dashboard'''
    return render(request, 'admin/base_layout.html')

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
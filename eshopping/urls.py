"""
URL configuration for eshopping project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('register/', views.CustomerRegistration.as_view(),
         name='customerregistration'),
    path('login/', views.CustomerLogin.as_view(), name='customerlogin'),
    path('logout/', views.customer_logout, name='logout'),
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('products/<int:id>/detail', views.detail, name='detail'),
    path('contact/', views.contact, name='contact'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/',
         views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_id>/<str:action>',
         views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/create/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/pay-by-mpesa', views.pay_order, name='pay_order'),
    path('orders/<int:order_id>/payment-confirmation',
         views.mpesa_callback, name='payment_confirmation'),
    path('payments/<str:transaction_id>/confirmation',
         views.query_transaction_status, name='transaction_status'),
    path('admin/',views.admin_dashboard, name = 'admin_dashboard'),
    path('admin/products/', views.list_admin_products, name='admin_products'),
    path('admin/products/create/', views.create_product, name='admin_create_product'),
    path('admin/products/<int:id>/edit/', views.edit_product, name='edit_product'),
    path('admin/products/<int:id>/delete/',
         views.delete_product, name='delete_product'),
    path('admin/categories/', views.create_category, name='admin_categories'),
    path('admin/categories/<int:id>/edit', views.edit_category, name='edit_category'),
    path('admin/categories/<int:id>/delete', views.delete_category, name='delete_category'),
    path('admin/sizes/', views.create_size, name='size_listing'),
    path('admin/sizes/<int:id>/edit',
         views.edit_size, name='edit_size'),
    path('admin/sizes/<int:id>/delete',
         views.delete_size, name='delete_size'),
    path('admin/colors/', views.create_color, name='color_listing'),
    path('admin/colors/<int:id>/edit',
         views.edit_color, name='edit_color'),
    path('admin/colors/<int:id>/delete',
         views.delete_color, name='delete_color'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






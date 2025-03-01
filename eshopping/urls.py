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
    path('admin/', admin.site.urls),
    path('register/', views.CustomerRegistration.as_view(),
         name='customerregistration'),
    path('login/', views.CustomerLogin.as_view(), name='customerlogin'),
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('products/<int:id>/detail', views.detail, name='detail'),
    path('contact/', views.contact, name='contact'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),
    path('cart/<int:cart_id>/delete', views.delete_cart_item, name='delete_cart_item'),
    path('cart/<int:cart_id>/update', views.update_cart_qty,
         name='update_cart_quantity'),
    path('category/<slug:val>',views.CategoryView.as_view(),name='category'),
    path('logout/', views.customer_logout, name='logout'),
    path('payment/',views.payment, name = 'payment'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






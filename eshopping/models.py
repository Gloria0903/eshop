from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = (
    ('MN', 'Mens_clothing'),
    ('WN', 'Womens_clothing'),
    ('BC', 'Babys_clothing'),
    ('SH', 'Shirts'),
    ('JE', 'Jeans'),
    ('SW', 'Swimwear'),
    ('SL', 'Sleepingwear'),
    ('SP', 'Sportswear'),
    ('JP', 'Jumpsuits'),
    ('BL', 'Blazers'),
    ('JK', 'Jackets'),
    ('SH', 'Shoes'),

)


class Products(models.Model):
    title = models.CharField(max_length=180)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodeshopping = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to='product')

    def __str__(self):
        return self.title


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()

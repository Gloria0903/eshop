'''model file'''
import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
# from django.contrib.auth.models import User



class CustomerManager(BaseUserManager):
    '''my manager'''
    def create_user(self,email, password):
        '''create normal user'''
        if not email:
            raise  ValueError('user must have an email address.')
        user =self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self,email, password):
        '''create super user: admin'''
        user = self.create_user(
            email = self.normalize_email(email),
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user



CATEGORY_CHOICES = (
    ('MN', 'Mens_clothing'),
    ('WN', 'Womens_clothing'),
    ('BC', 'Babys_clothing'),
    ('SH', 'Shirts'),
    ('JE', 'Jeans'),
    ('SW', 'Swimwear'),
    ('SL', 'Sleeping_wear'),
    ('SP', 'Sportswear'),
    ('JP', 'Jumpsuits'),
    ('BL', 'Blazers'),
    ('JK', 'Jackets'),
    ('SH', 'Shoes'),

)


class Products(models.Model):
    '''Product model'''
    title = models.CharField(max_length=180)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodeshopping = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to='product')

    def _str_(self):
        return f"{self.title}"

    @classmethod
    def get_all_products_by_category_id(cls, category_id):
        '''get products by category'''
        #pylint: disable = W0107
        pass

    @classmethod
    def get_all_products(cls):
        '''gets products'''
        #pylint: disable = W0107
        pass


# category models
class Category(models.Model):
    '''Category model'''
    name = models.CharField(max_length=50)

    @staticmethod
    def get_all_categories():
        '''gets all categories'''
        #pylint: disable = E1101
        return Category.objects.all()

    def _str_(self):
        return f"{self.name}"


# customer models



class Customer(AbstractUser, PermissionsMixin):
    '''Customer model'''
    phone = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    username = None

    objects = CustomerManager()
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []


    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    # Specify unique related_name for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='customer_groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='customer_user_permissions',
    )

    # to save the data
    def register(self):
        '''register's customer'''
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        '''get customer email'''
        return Customer.objects.filter(email__iexact=email).first()

    def is_exists(self):
        '''checks if customer exist'''
        #pylint: disable = E1101
        return Customer.objects.filter(email=self.email).exists()



class Order(models.Model):
    '''Order model'''
    product = models.ForeignKey(Products,
                                on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,
                                on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    address = models.CharField(max_length=50, default='', blank=True)
    phone = models.CharField(max_length=50, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def place_order(self):
        '''for placing order'''
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        '''gets customer orders'''
        #pylint: disable = E1101
        return Order.objects.filter(customer=customer_id).order_by('-date')

from django.db import models
class AccessToken(models.Model):
    app_label = 'django_daraja'  # Replace 'django_daraja' with the actual app name if different

    # Other fields of the AccessToken model


from django.db import models

class MpesaTransaction(models.Model):
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=50, unique=True)
    reference_number = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    # Add more fields as needed (e.g., status, error_code, error_message)


from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def _str_(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.selling_price
'''model file'''
import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
# from django.contrib.auth.models import User



class CustomerManager(BaseUserManager):
    '''my manager'''
    def create_user(self,email, username, password):
        '''create normal user'''
        if not email:
            raise  ValueError('user must have an email address.')
        if not username:
            raise  ValueError('user must have a username.')
        user =self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self,email,username,password):
        '''create super user: admin'''
        user = self.create_user(
            email = self.normalize_email(email),
            username=username,
            password=password,
        )

        user.is_admin = True
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

    def __str__(self):
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

    def __str__(self):
        return f"{self.name}"


# customer models



class Customer(AbstractUser,PermissionsMixin):
    '''Customer model'''
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=150, unique=True, default=first_name)
    phone = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)

    objects = CustomerManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def has_perm(self, perm, obj=None):
        return self.is_admin

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

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

    def create_superuser(self, email, password):
        '''create super user: admin'''
        user = self.create_user(
            email = self.normalize_email(email),
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Customer(AbstractUser, PermissionsMixin):
    '''Customer model'''
    phone = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    username = None
    profile_pic = models.ImageField(upload_to='profiles', default='profiles/default.png')

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
        # pylint: disable = E1101
        return Customer.objects.filter(email=self.email).exists()
    
    def order_count(self):
        '''counts orders'''
        return self.orders.count()

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


class Category(models.Model):
    '''Category model'''
    name = models.CharField(max_length=50)

    @staticmethod
    def get_all_categories():
        '''gets all categories'''
        return Category.objects.all()

    def __str__(self):
        return f"{self.name}"


class Size(models.Model):
    '''Size model'''
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"
    
    @staticmethod
    def get_all_sizes():
        '''gets all sizes'''
        return Size.objects.all()

class Color(models.Model):
    '''Color model'''
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def get_all_colors():
        '''gets all colors'''
        return Color.objects.all()

class ProductSizeColor(models.Model):
    '''ProductSizeColor model'''
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    size = models.ForeignKey('Size', on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey('Color', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product} - {self.size or 'No Size'} - {self.color or 'No Color'}"

class Product(models.Model):
    '''Product model'''
    title = models.CharField(max_length=180)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    product_image = models.ImageField(upload_to='product')
    categories = models.ManyToManyField(Category)
    sizes = models.ManyToManyField(Size, through=ProductSizeColor, blank=True)
    colors = models.ManyToManyField(Color, through=ProductSizeColor, blank=True)

    # def __str__(self):
    #     return f"{self.title}"


class Cart(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    product_size_color = models.ForeignKey(ProductSizeColor, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    colorVariation = models.CharField(max_length=50, null=True)
    sizeVariation = models.CharField(max_length=50, null=True)

    def total_price(self):
        return self.quantity * self.product.selling_price


class Order(models.Model):
    '''Order model'''
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    address = models.CharField(max_length=255, default='', blank=True)
    totalAmount = models.FloatField()
    phone = models.CharField(max_length=50, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    isPaid = models.BooleanField(default=False)

    def place_order(self):
        '''for placing order'''
        self.save()
    
    def order_items_count(self):
        '''counts order items'''
        return self.order_items.count()

    @staticmethod
    def get_orders_by_customer(customer_id):
        '''gets customer orders'''
        return Order.objects.filter(customer=customer_id).order_by('-date')


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(default=0)

    def total_price(self):
        return self.quantity * self.product.selling_price


class Payment(models.Model):
    '''Payment model'''
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amountPaid = models.FloatField(default=0)
    transactionId = models.CharField(max_length=255)
    transactionDate = models.DateField(null=True)
    receiptNumber = models.CharField(max_length=255, null=True)
    referencePhoneNumber = models.CharField(max_length=255, null=True)
    resultDesc = models.CharField(max_length=255, null=True)
    resultCode = models.CharField(max_length=255, null=True)
    responseReceived = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=255, default='Mpesa')
    status = models.CharField(choices=(
        ('PENDING', 'PENDING'),
        ('COMPLETED', 'COMPLETED'),
        ('FAILED', 'FAILED'),
    ), max_length=50, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)


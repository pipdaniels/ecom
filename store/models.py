import secrets

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Customer(User):
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE, related_name='_ptr')
    # name = models.CharField(max_length=50)
    # email = models.EmailField()
    phone_number = models.CharField(max_length=14, null=True)
    # user_ptr = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, default=0, null=True, decimal_places=2)
    is_digital = models.BooleanField(default=False, null=False, blank=True)
    image = models.ImageField(upload_to='uploads', null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time_of_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    # quantity = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-time_of_order']

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.is_digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=1000, null=False)
    city = models.CharField(max_length=1000, null=False)
    state = models.CharField(max_length=1000, null=False)
    zip_code = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name_plural = 'Shipping Address'
        ordering = ['-date_added']


class Payment(models.Model):
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=200)
    verified = models.BooleanField(default=False)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.amount

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_reference = Payment.objects.filter(ref=ref)
            if not object_with_similar_reference:
                self.ref = ref
        super().save(*args, **kwargs)

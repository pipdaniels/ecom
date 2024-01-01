from django.contrib import admin
from .models import *

# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'time_of_order', 'complete', 'transaction_id')
    empty_list = ['empty-data']



class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'slug')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'is_digital', 'image')


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'order', 'quantity', 'date_added')


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'phone', 'address', 'city', 'order', 'state', 'zip_code', 'date_added')


admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(Category, CategoryAdmin)

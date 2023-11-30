from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder


# Create your views here.
def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items': items, "order": order, 'cartItems': cartItems}
    return render(request, 'cart.html', context)



def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    context = {'items': items, "order": order, 'cartItems': cartItems}
    return render(request, 'checkout.html', context)


def store(request):
    data = cartData(request)
    items = data['items']
    # order = data['order']
    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems, 'items': items}
    return render(request, 'store.html', context)


def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('productId:', productId),
    print('action:', action)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity +1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity -1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added successfully', safe=False)


def processOrder(request):
    print('Data:', request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        Total = data['form']['total']
        order.transaction_id = transaction_id

        if Total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['form']['address'],
                city=data['form']['city'],
                state=data['form']['state'],
                zip_code=data['form']['zip_code'],
            )
    else:
        customer, order = guestOrder(request, data)

    Total = data['form']['total']
    order.transaction_id = transaction_id

    if Total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['form']['address'],
            city=data['form']['city'],
            state=data['form']['state'],
            zip_code=data['form']['zip_code'],
        )
    # send_mail(
    #     'Order Received',
    #     'Your order with ID;' 'transaction_id' 'has been received',
    #     'sales@riboto.com',
    #     customer,
    #           )
    return JsonResponse('The order was received and Payment Complete', safe=False)

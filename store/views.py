from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from . forms import RegisterForm
from django.contrib.auth import login, logout, authenticate





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
    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added successfully', safe=False)


def processOrder(request):
    # Print the data received in the request body
    print('Data:', request.body)

    # Generate a unique transaction_id using the current timestamp
    transaction_id = datetime.datetime.now().timestamp()

    # Parse the JSON data from the request body
    data = json.loads(request.body)

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # If authenticated, get the customer associated with the user
        customer = request.user

        # Get or create an order for the customer that is not complete
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Extract total from the form data
        Total = data['form']['total']

        # Set the transaction_id for the order
        order.transaction_id = transaction_id

        # Check if the total matches the cart total
        if Total == order.get_cart_total:
            order.complete = True

        # Save the order
        order.save()

        # If the order has a shipping address, create a ShippingAddress object
        if order.shipping:
            try:
                ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    address=data['shippingInfo']['address'],
                    city=data['shippingInfo']['city'],
                    state=data['shippingInfo']['state'],
                    zip_code=data['shippingInfo']['zip_code'],
                    phone=data['shippingInfo']['phone']
                    )
            except Exception as e:
                print(f"Error saving shipping address: {e}")

    else:
        # If the user is not authenticated, use a guestOrder function to get customer and order
        customer, order = guestOrder(request, data)

    # Reassign Total from the form data
    Total = data['form']['total']

    # Set the transaction_id for the order
    order.transaction_id = transaction_id

    # Check if the total matches the cart total
    if Total == order.get_cart_total:
        order.complete = True

    # Save the order
    order.save()

    # If the order has a shipping address, create a ShippingAddress object
    if order.shipping:
        try:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zip_code=data['shipping']['zip_code'],
                phone=data['shipping']['phone']
                )
        except Exception as e:
            print(f"Error saving shipping address: {e}")


    # Return a JsonResponse indicating that the order was received and payment is complete
    return JsonResponse('The order was received and Payment Complete', safe=False)

def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request, user)
            return redirect('cart')
    else:
        form = RegisterForm()
    return render(request, 'registration/sign_up.html', {'form': form})
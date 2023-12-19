from .models import *
import json
from django.core.mail import send_mail, mail_admins
from store.settings import EMAIL_HOST_USER

def cookieCart(request):
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        print('Cart:', cart)

        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0, 'Shipping': False}
        cartItems = order['get_cart_items']

        for i in cart:
            try:
                cartItems += cart[i]['quantity']

                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])

                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'image': product.image,
                    },
                    'quantity': cart[i]['quantity'],
                    'get_total': total,
                }
                items.append(item)

                if product.is_digital == False:
                    order['Shipping'] = True
            except:
                pass

        return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData (request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    print('User is not logged in...')
    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']
    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(product=product, order=order, quantity=item['quantity'])

    return customer, order

subject = 'Order Received'
message = 'Dear' + data['customer'] + 'Your order with the transaction ID: '+str(transaction_id)+ 'has been received succesfully. Expect the delivery in the shortest time possible. Thanks for shopping on Riboto!'
EMAIL_HOST_USER
email = data['form']['email']
recipient_list = [email]
send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)


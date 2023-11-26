from .models import *
import json


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
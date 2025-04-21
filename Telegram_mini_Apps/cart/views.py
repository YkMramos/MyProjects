from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse

import json

from Teleapp.models import ProductVariant, VariantImage
from .cart import Cart




@require_POST
@csrf_exempt
def update_product_quantity(request, product_id = None):

    try:
        if product_id == None:
            data = json.loads(request.body)
            product_id = int(data['product_id'])
            

            cart = Cart(request)
            quantity, price = cart.add_sub_remove(product = product_id, 
                                types = data['action'],
                                current_quantity = data['quantity'] )


            return JsonResponse({
                'status': 'success', 
                'quantity': quantity,
                'price': str(price),
                'total_price': cart_total(request, True)
            })
            


        data = json.loads(request.body)
       
        if data['action'] == 'add_to_cart' or data['action'] == 'increase' or data['action'] == 'buy_now_increase':
            quantity, total_count = cart_add(request, product_id)
        
        
        elif data['action'] == 'decrease':
            quantity, total_count = cart_subtract(request, product_id) 
        
        elif data['action'] == 'remove':
            quantity, total_count = cart_remove(request, product_id)



        return JsonResponse({
        'status': 'success', 
        'quantity': quantity,
        'total_price': cart_total(request, True),
        'total_count': total_count
    })

    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)



@require_POST
@csrf_exempt
def cart_total(request, action = None):
    try:
        data = request.session.get('cart', []) 
        total = 0

        for index, value in data.items():
            total +=  value['price']

        if action:
            return total
        
        return JsonResponse({
            'status': 'success',
            'total_price': str(total)
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })



@csrf_exempt
def cart_add(request, product_id):
    data = json.loads(request.body)
    cart = Cart(request)
    product = get_object_or_404(ProductVariant, id = product_id)


    if product:
        quantity = cart.add(product=product,
                quantity=data['quantity'],
                override_quantity = True               
                )
    
    return quantity
    

@csrf_exempt
def cart_subtract(request, product_id):
    data = json.loads(request.body)
    cart = Cart(request)
    product = get_object_or_404(ProductVariant, id = product_id)

    quantity = cart.subtract(product, quantity=data['quantity'])
    return quantity


@csrf_exempt
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(ProductVariant, id=product_id)
    quantity, total= cart.remove(product)

    return quantity,  total
    



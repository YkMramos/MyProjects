from decimal import Decimal
from django.conf import settings
from Teleapp.models import Product, VariantImage, ProductVariant, IMAGE_PRODUCT
from  django.shortcuts import get_object_or_404 





class Cart:
    def __init__(self, request):

        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def __iter__(self):

        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in = product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())



    def add_sub_remove(self, product, types, current_quantity):
        
        if types == 'increase':
            self.cart[str(product)]['quantity'] = current_quantity
            self.cart[str(product)]['price'] += float(self.cart[str(product)]['one_price'])
        
        elif types == 'decrease':
            self.cart[str(product)]['quantity'] = current_quantity
            self.cart[str(product)]['price'] -= float(self.cart[str(product)]['one_price'])
            
        elif types == 'remove':
            del self.cart[str(product)]
            self.save()
            return None, None
        
        
        self.save()
        

        return self.cart[str(product)]['quantity'], self.cart[str(product)]['price']




    def add(self, product, quantity=1, override_quantity = True):

        if str(product.id) not in self.cart:
            images_object = []
            product_variant = VariantImage.objects.filter(id=product.base_product.id).first()          
            model = Product.objects.filter(title=product_variant.base_product.title).first()
            quality_id = ProductVariant.objects.filter(id = product.id).first()
            images = IMAGE_PRODUCT.objects.filter(base_product = quality_id.base_product)
            tumbler_values = ProductVariant.objects.filter(id=product.id).values('tumbler1', 'tumbler2', 'tumbler3', 'tumbler4').first()
            tumbler_values = {key: value for key, value in tumbler_values.items() if value} if tumbler_values else {}

            for element in images:
                images_object.append(element.image.url)


            self.cart[str(product.id)] = { 
                'model_id': model.obj_id,
                'model_name': model.title,
                'category': model.category,
                'quality': product_variant.variant_name,
                'quality_id':quality_id.id,
                'tumblers': tumbler_values,
                'quantity': quantity,
                'price': float(product.price),
                'one_price': float(product.price),
                'card_image': images_object
            }


            total_quantity = sum(item['quantity'] for item in self.cart.values())
            self.save()
            
            return self.cart[str(product.id)]['quantity'], total_quantity
        
        
        if override_quantity:
            self.cart[str(product.id)]['quantity'] = quantity
            self.cart[str(product.id)]['price'] += float(product.price)
        else:
            self.cart[str(product.id)]['quantity'] += quantity 
        
        total_quantity = sum(item['quantity'] for item in self.cart.values())
        self.save()

        return self.cart[str(product.id)]['quantity'], total_quantity
    
    
    def subtract(self, product, quantity=1):

        self.cart[str(product.id)]['quantity'] = quantity
        self.cart[str(product.id)]['price'] -= float(product.price)
        self.save()  
        
        total_quantity = sum(item['quantity'] for item in self.cart.values())


        return self.cart[str(product.id)]['quantity'], total_quantity



    def remove(self, product):
        
        del self.cart[str(product.id)]
        self.save()
        total_quantity = sum(item['quantity'] for item in self.cart.values())
        return 0, total_quantity 
        
    def save(self):
        self.session.modified = True

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()







    
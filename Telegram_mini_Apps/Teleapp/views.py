import json
from django.db.models import Min, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.shortcuts import render

from .models import Product, ProductVariant, VariantImage, IMAGE_PRODUCT, RecommendationBlock




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



CATEGORY_CHOICES = [
        ('phones', 'Телефоны'),
        ('tablets', 'Планшеты'),
        ('laptops', 'Ноутбуки'),
        ('accessories', 'Аксессуары'),
        ('headphones', 'Наушники'),
        ('watches', 'Часы'),
    ]


def telegram_miniapp(request):
    products = Product.objects.all()
    recommendation_blocks = RecommendationBlock.objects.filter(is_active=True).order_by('order').prefetch_related(
            'variants__base_product',
            'variants__product_images',
            'variants__product_variants'
        )

    blocks_data = {}
    
    for block in recommendation_blocks:
        block_info = {
            "title": block.title,
            "description": block.catalog_description,
            "is_active": block.is_active,
            "variants": []
        } 
        
        for variant in block.get_available_variants():
            variant_info = {
                "full_title": f"{variant.base_product.title} - {variant.variant_name}",
                "base_product_available": variant.base_product.available,
                "images": [{"url": image.image.url} for image in variant.product_images.all()],
                "product_variants": [{"id": pv.id, "is_available": pv.is_available} for pv in variant.product_variants.filter(is_available=True)],
                "base_product_id": variant.base_product.obj_id  # Добавляем ID для URL
            }
            block_info["variants"].append(variant_info)
        
        blocks_data[block.order] = block_info
    
    session_cart = request.session.get('cart', {}) 
    total_quantity = sum(item['quantity'] for item in session_cart.values())
    
    return render(request, 'bases/product_catalog.html', {'products':products,
                                                        'CATEGORY_CHOICES': CATEGORY_CHOICES,
                                                         'total_quantity': total_quantity,
                                                         'blocks_data': blocks_data
                                                         })

def products(request):
    products = Product.objects.all()
    
    return render(request,
                'miniapp/products.html',
                {'products':products},)



def page(request, pk):

    tumblers = []

    obj_choice = ProductVariant.objects.get(id=pk)  # Поиск по запрашиваемому pk (вывод тумблеров, цены и базового id к каком варианту он принадлежит)
    product = VariantImage.objects.get(id = obj_choice.base_product.id) # Цвет  
    
    product_images = IMAGE_PRODUCT.objects.filter(base_product = obj_choice.base_product.id) #Изображения    
    base_product = Product.objects.get(obj_id=product.base_product.obj_id) 
    product_colors = VariantImage.objects.filter(base_product = base_product.obj_id)
    tumblers = ProductVariant.objects.filter(base_product = product.id)   

    session_cart = request.session.get('cart', {}) 
    total_quantity = sum(item['quantity'] for item in session_cart.values()) 
    
    try:
        quantity = session_cart[str(obj_choice.id)]['quantity']
    except KeyError:
        quantity = 0

    return render(request, 'bases/page.html', {'base_id': base_product.obj_id,
                                                'base_product': base_product, #Базовые характеристики модели
                                                'product_tumblers': tumblers, #Общий вывод всех тумблеров, бе
                                                 'product': product_colors, #Все цвета
                                                 'product_images': product_images, # Вывод изображений конкретной модели (вывод доп изображений)
                                                  'obj_choice': obj_choice, # Вывод конкретного товара, который мы обозначили (стоимость и количетсво памяти)
                                                  'specs': base_product.specs, #Характеристики
                                                    'obj_color': product.variant_name,
                                                  'quantity': quantity, 
                                                  'total_quantity': total_quantity,
                                                  'category': base_product.category,
                                                  }) 



@csrf_exempt
def update_product_page(request, pk):
    data = json.loads(request.body)

    obj_choice = VariantImage.objects.get(
        base_product_id=pk,
        variant_name=data['color']
    )

    product_title = obj_choice.base_product.title
    images = IMAGE_PRODUCT.objects.filter(base_product=obj_choice)
    images_card = [{"url": i.image.url} for i in images if i.image]
    
    data_tumblers = ProductVariant.objects.filter(base_product=obj_choice.id)
    tumblers = [{i.id: i.tumbler1} for i in data_tumblers if i.tumbler1]
    
    try:
        variants = ProductVariant.objects.get(
            base_product=obj_choice.id,
            tumbler1=data['memory']
        )
    except ProductVariant.DoesNotExist:
        if tumblers:
            variant_id = min(key for d in tumblers for key in d)
            variants = ProductVariant.objects.get(id=variant_id)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Нет доступных вариантов товара'
            })

    session_cart = request.session.get('cart', {}) 
    try:
        quantity = session_cart[str(variants.id)].get('quantity', 0)
    except (IndexError, KeyError, TypeError):
        quantity = 0

    product_full_name = f"{product_title} {obj_choice.variant_name} {variants.tumbler1}"

    return JsonResponse({
        'status': 'success',
        'images': images_card,
        'title': product_full_name,
        'price': variants.price,
        'obj_id': variants.id,
        'quantity': quantity,
        'product_tumblers': tumblers
    })



@csrf_exempt
def search_category_price(products):
    variant_images = VariantImage.objects.filter(
    base_product__in=products,
    default_obj=True
)
    result = ProductVariant.objects.filter(
    base_product__in=variant_images
).values(
    title = F('base_product__base_product__title'),  # название продукта
    base_id = F('base_product__id'),  # ID варианта изображения
    image = F('base_product__base_product__image')
).annotate(
    price=Min('price')  # минимальная цена для каждого варианта
)   
    return result


@csrf_exempt
def quantity_search_cart(session_cart, products):
    products_list = list(products)
    
    # Проходим по каждому продукту
    for product in products_list:
        # Проверяем, есть ли продукт в корзине по base_id
        cart_item = session_cart.get(str(product['base_id']))
        if cart_item:
            # Если продукт найден в корзине, добавляем quantity
            product['quantity'] = cart_item['quantity']
        else:
            # Если продукта нет в корзине, устанавливаем quantity в 0
            product['quantity'] = 0

    return products_list




def transform_products_data(products_queryset, session_cart):
    result = {}
    
    for product in products_queryset:
        # Создаем множество для хранения уже обработанных variant_id
        processed_variants = set()
        
        if product.obj_id not in result:
            result[product.obj_id] = []
            
        # Получаем все варианты для продукта через related_name
        for variant_image in product.variant_images.all():
            for variant in variant_image.product_variants.all():
                # Пропускаем уже обработанные варианты
                if variant.id in processed_variants:
                    continue
                    
                processed_variants.add(variant.id)
                
                # Получаем изображения для текущего variant_image

                images = variant_image.product_images.all().order_by('order')
                image_paths = [img.image.url for img in images]
                name = variant_image
                tumbler_all = {
                    'tumbler2': variant.tumbler2,
                    'tumbler3': variant.tumbler3,
                    'tumbler4': variant.tumbler4
                }

                
                
                # Базовые значения
                stock_quantity = variant.stock
                cart_quantity = 0
                total_price = float(0)
                
                # Проверяем наличие данных в сессии
                for cart_item in session_cart.values():
                    if cart_item.get('quality_id') == variant.id:
                        cart_quantity = cart_item.get('quantity', 0)
                        total_price = cart_item.get('price', float(0))
                
                variant_data = {
                    'model_name': product.title,
                    'title' : name,
                    'quality_id': variant.id,
                    'tumbler1': variant.tumbler1,
                    'tumbler_all': tumbler_all,
                    'image': image_paths,
                    'stock_quantity': stock_quantity,
                    'cart_quantity': cart_quantity,
                    'price': variant.price,
                    'total_price': total_price
                }
                
                result[product.obj_id].append(variant_data)
    
    return result



def search_products(request, pk):
    query = request.GET.get('query', '')
    products = []
    
    if query:
        products = Product.objects.filter(title__icontains=query, category = pk )

    session_cart = request.session.get('cart', {}) 
    products = transform_products_data(products, session_cart)
    query_search = True
    total_quantity = sum(item['quantity'] for item in session_cart.values())

    if products:
        In_stock = True
    else:
        In_stock = False

    return render(request, 'bases/category.html', {'products': products, 
                                                   'cart': session_cart,
                                                   'total_quantity': total_quantity,
                                                   'category': pk,
                                                   'query_search': query_search,
                                                   'In_stock': In_stock})




def category_catalog(request, pk):

    products = Product.objects.filter(category=pk)
    session_cart = request.session.get('cart', {}) 
    products = transform_products_data(products, session_cart)
    query_search = False
    total_quantity = sum(item['quantity'] for item in session_cart.values())
    
    if products:
        In_stock = True
    else:
        In_stock = False

    return render(request, 'bases/category.html', {'products': products, 
                                                   'cart': session_cart,
                                                   'total_quantity': total_quantity,
                                                   'category': pk,
                                                   'query_search': query_search,
                                                   'In_stock': In_stock
                                                   })



def cart_shopping(request):
    products = request.session.get('cart', []) 
    return render(request, 'cart/shopping_cart.html', {'product': products})



def checkout_page(request):

    return render(request, 'cart/checkout_page.html')

def pay_deliry(request):
    return render(request, 'FAQ/pay_deliry.html')

def contacts(request):

    return render(request, 'FAQ/contacts.html')

def guarantee(request):
    return render(request, 'FAQ/guarantee.html')







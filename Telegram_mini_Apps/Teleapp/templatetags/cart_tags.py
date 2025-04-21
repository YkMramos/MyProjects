from django import template

register = template.Library()

@register.filter
def is_in_cart(cart_items, product):
    """
    Проверяет, есть ли продукт в корзине пользователя.
    """
    return cart_items.filter(product=product).exists()
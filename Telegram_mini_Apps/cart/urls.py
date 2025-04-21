
from . import views
from django.urls import path




urlpatterns = [

    #Здесь содержатся методы увелчинения, уменьшения и удаления товара из корзины
    path('update_product_quantity/<int:product_id>/', views.update_product_quantity, name='update_product_quantity'),
    path('cart_remove/<int:product_id>/', views.cart_remove, name='remove_from_cart'),
    # path('cart_datail/', cart_views.cart_detail, name = 'cart_detail'),
    
    
    path('cart_holder/', views.update_product_quantity, name ='cart_holder'),
    path('cart_total/', views.cart_total, name = 'cart_total'),
       
        ]


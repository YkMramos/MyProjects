from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from Teleapp import views as app_views
from Bot import views as bot_views



urlpatterns = [

    # Главная страница и админка
    path('',app_views.telegram_miniapp, name = 'telegram_miniapp'),
    path('admin/', admin.site.urls),

    # каталог определенной категории
    path('category/<str:pk>', app_views.category_catalog, name = 'category'),
    path('search/<str:pk>', app_views.search_products, name = 'search'),
   
    # страница товара
    path('page/<int:pk>/', app_views.page, name='page'),
    path('update_product_page/<int:pk>', app_views.update_product_page, name='update_product_page'),
    #Корзина покупок
    # path('checkout/<int:pk>', app_views.cart_shopping, name = 'checkout'),
    path('cart_shopping/', app_views.cart_shopping, name = 'shopping'),
    path('checkout_page/', app_views.checkout_page, name = 'checkout_page'),
    #страницы FAQ
    path('FAQ_pay_delivery/', app_views.pay_deliry, name = 'FAQ_pay_delivery'),
    path('FAQ_contacts/', app_views.contacts, name = 'FAQ_contacts'),
    path('FAQ_guarantee/', app_views.guarantee, name = 'FAQ_guarantee'),

    path('cart/', include('cart.urls')),
    path('webhook/', bot_views.webhook_handler, name='webhook_handler')

    
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




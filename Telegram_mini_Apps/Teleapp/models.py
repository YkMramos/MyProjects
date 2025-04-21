from django.db import models
from django.core.exceptions import ValidationError

import os

def default_specs():
    return {
        "key1": "arg",
        "key2": "arg",
        "key3": "arg"
    }

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('phones', 'Phones'),
        ('tablets', 'Tablets'),
        ('laptops', 'Laptops'),
        ('accessories', 'Accessories'),
        ('headphones', 'Headphones'),
        ('watches', 'Watches'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Категория")
    obj_id = models.AutoField(verbose_name="уникальный id товара", primary_key=True)
    image = models.ImageField(upload_to='media/products/%Y/%m/%d', verbose_name="Изображение карточки товара")
    description = models.TextField(verbose_name="Описание")
    specs = models.JSONField(verbose_name="Характеристики", default=default_specs)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    available = models.BooleanField(default=True, verbose_name="В наличии")

    class Meta:
        ordering = ['-created']
        verbose_name = 'Базовый товар'
        verbose_name_plural = 'Базовые товары'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['-created']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.specs:
            self.specs = {
                "key1": "arguments",
                "key2": "arguments",
                "key3": "arguments",
                "key4": "arguments",
                "key5": "arguments"
            }
        super().save(*args, **kwargs)

def get_variant_image_upload_path(instance, filename):
    return os.path.join('media/image', filename)

class VariantImage(models.Model):
    id = models.AutoField(verbose_name="уникальный id товара", primary_key=True)
    base_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variant_images')
    variant_name = models.CharField(max_length=50, verbose_name="title")
    default_obj = models.BooleanField(default=False)
    # sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок", null=True, blank=True)

    class Meta:
        # ordering = ['sort_order']
        verbose_name = 'Параметры товара'
        verbose_name_plural = 'Параметры товара' 
    
    def __str__(self):
        return f"{self.base_product.title} - {self.variant_name}"

class IMAGE_PRODUCT(models.Model):
    base_product = models.ForeignKey(VariantImage, on_delete=models.CASCADE, related_name='product_images')
    char_1 = models.CharField(max_length=50, verbose_name="Характеристика", blank=True, null=True)
    image = models.ImageField(upload_to=get_variant_image_upload_path, verbose_name="Изображение Продукта")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        ordering = ['order']
        verbose_name = 'для конкретного характеристики Модели'
        verbose_name_plural = 'для конкретного характеристики Модели' 

class ProductVariant(models.Model):
    base_product = models.ForeignKey(VariantImage, on_delete=models.CASCADE, related_name='product_variants')
    tumbler1 = models.CharField(max_length=50, verbose_name="tumbler1")
    tumbler2 = models.CharField(max_length=50, verbose_name="tumbler2", blank=True, null=True)
    tumbler3 = models.CharField(max_length=50, verbose_name="tumbler3", blank=True, null=True)
    tumbler4 = models.CharField(max_length=50, verbose_name="tumbler4", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество в наличии")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")

    class Meta:
        verbose_name = 'Тумблеры товара'
        verbose_name_plural = 'Тумблеры товара'
        unique_together = ['base_product', 'tumbler1', 'tumbler2', 'tumbler3', 'tumbler4']

    def __str__(self):
        return f"{self.base_product.base_product.title} - {self.tumbler1} {self.tumbler2 or ''}"
    








# Существующие модели остаются без изменений, обновляем только RecommendationBlock
class RecommendationBlock(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название блока")
    catalog_description = models.CharField(max_length=100, verbose_name="Описание блока", default="Описание по умолчанию")
    variants = models.ManyToManyField(VariantImage, verbose_name="Варианты товаров", related_name="recommendation_blocks")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        ordering = ['order']
        verbose_name = 'Блок рекомендаций'
        verbose_name_plural = 'Блоки рекомендаций'

    def __str__(self):
        return self.title

    def clean(self):
        total_items = self.variants.count()
        if total_items < 6 or total_items > 7:
            raise ValidationError("Блок должен содержать от 6 до 7 вариантов товаров.")

        # Проверка доступности базового товара и варианта
        for variant in self.variants.all():
            if not variant.base_product.available:
                raise ValidationError(f"Базовый товар '{variant.base_product.title}' для варианта '{variant}' не доступен.")
            if not variant.product_variants.filter(is_available=True).exists():
                raise ValidationError(f"Вариант '{variant}' не имеет доступных ProductVariant.")

    def get_available_variants(self):
        """Возвращает только доступные варианты, где Product.available=True и ProductVariant.is_available=True."""
        return self.variants.filter(
            base_product__available=True,
            product_variants__is_available=True
        ).distinct()


"""
Product - базовая информация о продукте
VariantImage - параметры товара
параметры данной модели:(variant_name - обязательный для заполнения)
 variant_name - отличительная характеристика на самом изображении
 base_product - базовый продукт с базовой информацией о товаре 
 default_obj - Дефолтный тип объекта
ProductVariant - тумблеры продукта (обязательный только один тумблер)
- продукт с параметром такими как (price, gb)
IMAGE_PRODUCT - Изображение товара для главной характеристики(главная характеристика, отличительная характеристика, визуальная характеритстика ) 
- Изображение и характеристика товара (необязательная)
"""


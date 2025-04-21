from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget
import json
from .models import VariantImage, ProductVariant, Product, IMAGE_PRODUCT, RecommendationBlock






class KeyValueWidget(AdminTextareaWidget):
    """
    Специальный виджет для удобного редактирования JSON-полей
    Позволяет вводить данные в формате ключ: значение через разделитель /
    """
    def format_value(self, value):
        if value is None or value == '':
            return ''
        try:
            if isinstance(value, dict):
                return '/'.join(f"{key}: {val}" for key, val in value.items())
            if isinstance(value, str):
                try:
                    value_dict = json.loads(value)
                    if isinstance(value_dict, dict):
                        return '/'.join(f"{key}: {val}" for key, val in value_dict.items())
                    return value
                except json.JSONDecodeError:
                    if '/' in value:
                        return value
                    return str(value)
            return str(value)
        except Exception as e:
            print(f"Ошибка форматирования значения: {e}")
            return str(value)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, '')
        if not value:
            return json.dumps({})
        try:
            json.loads(value)
            return value
        except json.JSONDecodeError:
            result = {}
            pairs = value.strip('/').split('/')
            for pair in pairs:
                if ':' in pair:
                    key, val = pair.split(':', 1)
                    result[key.strip()] = val.strip()
            return json.dumps(result)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'specs': KeyValueWidget(attrs={'cols': 80, 'rows': 5}),
        }

class PRODUCTImageInline(admin.TabularInline):
    model = IMAGE_PRODUCT
    extra = 1
    fields = ['image', 'char_1', 'order']
    show_change_link = True

class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1
    # fields = ['sort_order']
    show_change_link = True

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['tumbler1', 'tumbler2', 'tumbler3', 'tumbler4', 'price', 'stock', 'is_available']
    show_change_link = True

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['obj_id', 'title', 'available', 'created']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['available']
    search_fields = ['title', 'description']
    readonly_fields = ('obj_id',)
    date_hierarchy = 'created'
    save_on_top = True
    # inlines = [VariantImageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'category', 'obj_id', 'image', 'available', 'description', 'specs')
        }),
    )

@admin.register(VariantImage)
class VariantImageAdmin(admin.ModelAdmin):
    list_display = ['base_product', 'variant_name', 'default_obj']
    inlines = [ProductVariantInline, PRODUCTImageInline]



class RecommendationBlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'catalog_description', 'variant_count', 'available_variant_count', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    filter_horizontal = ['variants']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'catalog_description','order', 'is_active')
        }),
        ('Содержимое блока', {
            'fields': ('variants',),
            'description': 'Выберите от 6 до 7 вариантов товаров. Учитываются только варианты с доступным базовым товаром (Product.available=True) и доступным вариантом (ProductVariant.is_available=True).'
        }),
    )

    def variant_count(self, obj):
        return obj.variants.count()
    variant_count.short_description = 'Всего вариантов'

    def available_variant_count(self, obj):
        return obj.get_available_variants().count()
    available_variant_count.short_description = 'Доступных вариантов'

    def save_model(self, request, obj, form, change):
        obj.clean()
        super().save_model(request, obj, form, change)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "variants":
            # Ограничиваем выбор только доступными вариантами
            kwargs["queryset"] = VariantImage.objects.filter(
                base_product__available=True,
                product_variants__is_available=True
            ).distinct()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(RecommendationBlock, RecommendationBlockAdmin)
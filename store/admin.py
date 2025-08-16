from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = ('show_image', 'name', 'price', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    
    def show_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 10px;"/>', obj.image.url)
        return "No Image"

    show_image.short_description = "Image"

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)

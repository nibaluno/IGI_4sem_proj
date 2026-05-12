from django.contrib import admin
from .models import Category, Manufacturer, Product, Review

class ReviewInline(admin.TabularInline): 
    model = Review
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'date_added')
    list_filter = ('category', 'manufacturer')
    search_fields = ('name',)
    inlines = [ReviewInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)} 

admin.site.register(Manufacturer)
admin.site.register(Review)

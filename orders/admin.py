from django.contrib import admin
from .models import Order, OrderItem, PromoCode

#встроенное редактирование связанных записей
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1 # Количество пустых строк для добавления товара

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'created_at', 'status', 'delivery_date')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline] # Вот она магия!

admin.site.register(PromoCode)
admin.site.register(OrderItem)
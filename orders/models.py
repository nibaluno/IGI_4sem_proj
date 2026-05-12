from django.db import models
from django.conf import settings
from store.models import Product


class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Промокод")
    discount = models.IntegerField(verbose_name="Скидка (%)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    expiry_date = models.DateField(verbose_name="Срок действия")

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code
    

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processed', 'В обработке'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  related_name='orders', verbose_name="Клиент")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    delivery_date = models.DateField(verbose_name="Дата доставки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Промокод")


# Один заказ может содержать много товаров, и один товар может присутствовать во многих заказах
    products = models.ManyToManyField(Product, through='OrderItem', verbose_name="Товары")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.id} — {self.client.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на момент покупки")

    def save(self, *args, **kwargs):
        # Автоматически фиксируем цену товара при сохранении позиции заказа
        if not self.price_at_purchase:
            self.price_at_purchase = self.product.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"


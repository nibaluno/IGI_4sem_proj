from django.db import models
from django.conf import settings
from django.utils.text import slugify



class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="URL (slug)")
    description = models.TextField(blank=True, verbose_name="Описание")


    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории" 

    def __str__(self):
        return self.name
    


class Manufacturer(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название")
    country = models.CharField(max_length=100, verbose_name="Страна")
    logo = models.ImageField(upload_to='manufacturers/', blank=True, null=True, verbose_name="Логотип")

    class Meta:
        verbose_name = "Изготовитель"
        verbose_name_plural = "Изготовители"

    def __str__(self):
        return self.name
    


class Product(models.Model):
    UNIT_CHOICES = [('шт', 'Штуки'), ('кг', 'Килограммы'), ('л', 'Литры')]
    
    name = models.CharField(max_length=200, verbose_name="Название товара")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='products', verbose_name="Изготовитель")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, verbose_name="Единица измерения")
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток на складе")
    photo = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Фото")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"
    

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор") #Один ко многим
    #У одного отзыва может быть только один Автор.
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Оценка (1-5)")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
from django.db import models
from django.conf import settings

class CompanyInfo(models.Model):
    about_text = models.TextField(verbose_name="О компании")
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")
    logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name="Логотип")
    requisites = models.TextField(verbose_name="Реквизиты")

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

class CompanyHistory(models.Model):
    company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='history')
    year = models.PositiveIntegerField(verbose_name="Год")
    event = models.CharField(max_length=255, verbose_name="Событие")

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="Слаг (для URL)") 
    short_content = models.CharField(max_length=255, verbose_name="Краткое содержание")
    full_content = models.TextField(verbose_name="Полный текст")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Изображение")
    date_published = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

class Vacancy(models.Model):
    title = models.CharField(max_length=150, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    date_added = models.DateField(auto_now_add=True)
    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

class Contact(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Сотрудник")
    position = models.CharField(max_length=100, verbose_name="Должность")
    photo = models.ImageField(upload_to='contacts/', blank=True, null=True, verbose_name="Фото")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

class GlossaryTerm(models.Model):
    term = models.CharField(max_length=100, verbose_name="Термин")
    definition = models.TextField(verbose_name="Определение")
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Термин словаря"
        verbose_name_plural = "Словарь терминов"



class PrivacyPolicy(models.Model):
    content = models.TextField(verbose_name="Текст политики")
    class Meta:
        verbose_name = "Политика конфиденциальности"
        verbose_name_plural = "Политика конфиденциальности"
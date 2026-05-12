from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date


def validate_age_18(born_date):
    if born_date: 
        today = date.today()
        age = today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))
        if age < 18:
            raise ValidationError('Регистрация доступна только пользователям старше 18 лет.')


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Покупатель'),
        ('employee', 'Сотрудник'),
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
        message="Формат телефона: +375 (29) XXX-XX-XX"
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer', verbose_name="Роль")
    phone = models.CharField(validators=[phone_regex], max_length=20, blank=True, null=True, verbose_name="Телефон")
    birth_date = models.DateField(validators=[validate_age_18], blank=True, null=True, verbose_name="Дата рождения")
    
    address = models.CharField(max_length=250, blank=True, verbose_name="Адрес")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    timezone = models.CharField(max_length=50, default='Europe/Minsk', verbose_name="Часовой пояс")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        if full_name:
            return f"{full_name} ({self.get_role_display()})"
        return f"{self.username} ({self.get_role_display()})"
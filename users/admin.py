from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Колонки, которые видны в общем списке пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'city')
    # Боковая панель фильтров
    list_filter = ('role', 'city', 'is_staff', 'is_superuser')
    # Поиск по этим полям
    search_fields = ('username', 'phone', 'email', 'city')

    # Блоки полей при РЕДАКТИРОВАНИИ пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Информация профиля', {
            'fields': ('role', 'phone', 'birth_date', 'address', 'city', 'avatar', 'timezone'),
        }),
    )
    # Блоки полей при СОЗДАНИИ НОВОГО пользователя через админку
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Информация профиля', {
            'fields': ('role', 'phone', 'birth_date', 'city'),
        }),
    )
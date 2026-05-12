import os
import django
from datetime import date, timedelta
from django.utils import timezone

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser
from store.models import Category, Manufacturer, Product
from orders.models import Order, OrderItem
from info.models import News, Vacancy

def run_seed():
    print("Начинаем наполнение базы данных...")

    # Используем get_or_create (если есть - берет, если нет - создает)
    cat1, _ = Category.objects.get_or_create(slug="poroshki", defaults={'name': "Порошки"})
    cat2, _ = Category.objects.get_or_create(slug="geli", defaults={'name': "Гели"})
    man, _ = Manufacturer.objects.get_or_create(name="Henkel", defaults={'country': "Германия"})

    # Товары создаем только если их нет (для простоты)
    if Product.objects.count() == 0:
        products = []
        for i in range(15):
            p = Product.objects.create(
                name=f"Товар №{i+1}",
                category=cat1 if i % 2 == 0 else cat2,
                manufacturer=man,
                price=100 + i*10,
                unit='шт',
                stock=100
            )
            products.append(p)
        print("Создано 15 товаров.")
    else:
        products = list(Product.objects.all())

    # Клиенты - создаем через get_or_create по username
    cities = ["Минск", "Брест", "Гродно", "Витебск", "Гомель", "Могилев"]
    for i in range(12):
        username = f"buyer{i}"
        user, created = CustomUser.objects.get_or_create(username=username)
        if created:
            user.set_password('123')
            user.role = 'buyer'
            user.city = cities[i % len(cities)]
            user.save()
    print("Создано 12 клиентов.")

    # 4. Создаем 3 новости (для главной страницы)
    for i in range(3):
        News.objects.create(
            title=f"Новость №{i+1}",
            slug=f"novost-{i+1}",
            short_content="Краткое описание новости для теста.",
            full_content="Полный текст новости с подробностями."
        )
    print("Создано 3 новости.")

    # 5. Создаем 3 вакансии
    for i in range(3):
        Vacancy.objects.create(
            title=f"Вакансия №{i+1}",
            description="Требуется сотрудник на полный рабочий день."
        )
    print("Создано 3 вакансии.")

    # 6. Создаем заказы за последние 6 месяцев (для графиков)
    buyer = CustomUser.objects.filter(role='buyer').first()
    for i in range(6):
        order_date = timezone.now() - timedelta(days=i * 30)
        order = Order.objects.create(client=buyer, delivery_date=date.today() + timedelta(days=5))
        order.created_at = order_date
        order.save()
        
        # Добавляем случайные товары
        for p in products[:3]:
            OrderItem.objects.create(order=order, product=p, quantity=1, price_at_purchase=p.price)
    
    print("База наполнена успешно!")

if __name__ == '__main__':
    run_seed()
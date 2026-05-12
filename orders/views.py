from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, Sum, Count, F        # всё из db.models
from django.db.models.functions import TruncMonth, Coalesce     # Coalesce — отсюда!

from .models import Order, PromoCode, OrderItem
from store.models import Product, Category
from users.models import CustomUser
import json
import numpy as np
import statistics
from datetime import date
from decimal import Decimal

# --- 1. Промокоды ---

def promocode_list_view(request):
    active_promos = PromoCode.objects.filter(is_active=True)
    archive_promos = PromoCode.objects.filter(is_active=False)
    return render(request, 'orders/promocodes.html', {
        'active_promos': active_promos,
        'archive_promos': archive_promos,
    })


def promocode_create(request):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ запрещен")
    if request.method == "POST":
        p = PromoCode()
        p.code = request.POST.get("code")
        p.discount = request.POST.get("discount")
        p.expiry_date = request.POST.get("expiry_date")
        p.is_active = True
        p.save()
        return redirect('promocodes')
    return render(request, 'orders/promocode_form.html')


def promocode_edit(request, id):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ запрещен")
    p = get_object_or_404(PromoCode, id=id)
    if request.method == "POST":
        p.code = request.POST.get("code")
        p.discount = request.POST.get("discount")
        p.expiry_date = request.POST.get("expiry_date")
        p.is_active = request.POST.get("is_active") == 'on'
        p.save()
        return redirect('promocodes')
    return render(request, 'orders/promocode_form.html', {'promo': p})


def promocode_delete(request, id):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ запрещен")
    p = get_object_or_404(PromoCode, id=id)
    p.delete()
    return redirect('promocodes')


# --- 2. Детали заказа ---

@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk, client=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


def cart_view(request):
    return render(request, 'orders/cart.html')


# --- 3. Аналитика (Дашборд) ---

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ только для админа")

    context = {}

    # ── Прайс-лист по категориям ──────────────────────────────────
    context['categories'] = Category.objects.prefetch_related('products').all()

    # ── Клиенты по городам ────────────────────────────────────────
    clients_by_city = list(
        CustomUser.objects.filter(role='buyer')
        .values('city')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    context['clients_by_city'] = clients_by_city
    context['cities_labels'] = json.dumps(
        [item['city'] if item['city'] else 'Не указан' for item in clients_by_city]
    )
    context['cities_data'] = json.dumps([item['count'] for item in clients_by_city])

    # ── Список клиентов в алфавитном порядке ──────────────────────
    context['clients_alpha'] = CustomUser.objects.filter(role='buyer').order_by('last_name', 'first_name')

    # ── Самый популярный и непопулярный товар ─────────────────────
    product_sales = Product.objects.annotate(
        total_sold=Coalesce(Sum('orderitem__quantity'), 0)
    ).order_by('-total_sold')
    context['most_popular']  = product_sales.first()
    context['least_popular'] = product_sales.last()

    # ── Сводная таблица: виды продукции, объёмы, поступления ──────
    # Для каждого товара считаем: сколько продано штук и на какую сумму
    products_summary = Product.objects.annotate(
        total_qty=Coalesce(Sum('orderitem__quantity'), 0),
        total_revenue=Coalesce(
            Sum(F('orderitem__quantity') * F('orderitem__price_at_purchase')),
            Decimal('0'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).order_by('name')
    context['products_summary'] = products_summary

    # Общая сумма продаж по всем товарам (для итоговой строки)
    context['total_all_revenue'] = sum(float(p.total_revenue) for p in products_summary)
    context['total_all_qty']     = sum(p.total_qty for p in products_summary)

    # ── Ежемесячный объём продаж ──────────────────────────────────
# ── Ежемесячный объём продаж ──────────────────────────────────
    monthly_sales = list(          # <-- list() — обязательно!
        Order.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            total=Coalesce(
                Sum(F('orderitem__quantity') * F('orderitem__price_at_purchase')),
                Decimal('0'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            orders_count=Count('id')
        )
        .order_by('month')
    )
    context['monthly_sales'] = monthly_sales  # теперь список — итерируется сколько угодно раз

    months_labels = [m['month'].strftime('%b %Y') for m in monthly_sales if m['month']]
    sales_data    = [float(m['total']) for m in monthly_sales]

    # ── Годовой отчёт ─────────────────────────────────────────────
    context['annual_revenue'] = round(sum(sales_data), 2)

    # ── Годовой отчёт ─────────────────────────────────────────────
    context['annual_revenue'] = round(sum(sales_data), 2)

    # ── Прибыльная категория ──────────────────────────────────────
# ── Прибыльная категория ──────────────────────────────────────
    profitable_cats = list(        # <-- list() — обязательно!
        Category.objects.annotate(
            revenue=Coalesce(
                Sum(F('products__orderitem__quantity') * F('products__orderitem__price_at_purchase')),
                Decimal('0'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            qty=Coalesce(Sum('products__orderitem__quantity'), 0)
        ).order_by('-revenue')
    )
    context['most_profitable_cat'] = profitable_cats[0] if profitable_cats else None
    context['profitable_cats']     = profitable_cats
    context['cat_labels']  = json.dumps([c.name for c in profitable_cats])
    context['cat_revenue'] = json.dumps([float(c.revenue) for c in profitable_cats])

    # ── Статистика: среднее, медиана, мода по сумме продаж ────────
    orders_totals = list(
        Order.objects.annotate(
            total=Coalesce(
                Sum(F('orderitem__quantity') * F('orderitem__price_at_purchase')),
                Decimal('0'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).values_list('total', flat=True)
    )

    if orders_totals:
        totals_float = [float(x) for x in orders_totals]
        context['mean_sales']   = round(statistics.mean(totals_float), 2)
        context['median_sales'] = round(statistics.median(totals_float), 2)
        try:
            context['mode_sales'] = round(statistics.mode(totals_float), 2)
        except statistics.StatisticsError:
            context['mode_sales'] = 'Нет моды'
    else:
        context['mean_sales'] = context['median_sales'] = context['mode_sales'] = 0

    # ── Статистика: средний и медиана возраст клиентов ────────────
    buyers = CustomUser.objects.filter(role='buyer', birth_date__isnull=False)
    today  = date.today()
    ages   = [
        today.year - b.birth_date.year
        - ((today.month, today.day) < (b.birth_date.month, b.birth_date.day))
        for b in buyers
    ]
    if ages:
        context['mean_age']   = round(statistics.mean(ages), 1)
        context['median_age'] = statistics.median(ages)
    else:
        context['mean_age'] = context['median_age'] = 'Нет данных'

 # ── Линейный тренд + прогноз (numpy) ─────────────────────────
    trend_data = []
    forecast   = 0
    if len(sales_data) > 1:
        x = np.arange(len(sales_data))
        y = np.array(sales_data)
        k, b = np.polyfit(x, y, 1)
        trend_data = [round(float(k * xi + b), 2) for xi in x]
        forecast   = round(float(k * len(sales_data) + b), 2)

    # ── Передаём в шаблон чистые списки (json_script сам сериализует) ──
    context['months_labels']  = months_labels                # список строк
    context['sales_data']     = sales_data                   # список float
    context['trend_data']     = trend_data                   # список float
    context['cat_labels']     = [c.name for c in profitable_cats]
    context['cat_revenue']    = [float(c.revenue) for c in profitable_cats]
    context['cities_labels']  = [item['city'] if item['city'] else 'Не указан' for item in clients_by_city]
    context['cities_data']    = [item['count'] for item in clients_by_city]
    context['forecast']       = max(forecast, 0)
    context['annual_revenue'] = round(sum(sales_data), 2)

    return render(request, 'orders/admin_dashboard.html', context)




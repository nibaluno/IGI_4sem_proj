from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, Sum, Count, F
from django.db.models.functions import TruncMonth, Coalesce

from .models import Order, PromoCode, OrderItem
from store.models import Product, Category
from users.models import CustomUser

import numpy as np
import statistics
from datetime import date
from decimal import Decimal

# --- Импорты для Matplotlib ---
import matplotlib
matplotlib.use('Agg')  # Обязательно для серверов (чтобы не пытался открыть окно на экране)
import matplotlib.pyplot as plt
import io
import base64

def get_graph():
    """Вспомогательная функция для конвертации графика в Base64"""
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')
    plt.close() # Очищаем память
    return graphic

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


# --- 3. Аналитика (Дашборд с Matplotlib) ---
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ только для админа")

    context = {}

    context['categories'] = Category.objects.prefetch_related('products').all()

    clients_by_city = list(
        CustomUser.objects.filter(role='buyer')
        .values('city')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    context['clients_by_city'] = clients_by_city
    context['clients_alpha'] = CustomUser.objects.filter(role='buyer').order_by('last_name', 'first_name')

    product_sales = Product.objects.annotate(
        total_sold=Coalesce(Sum('orderitem__quantity'), 0)
    ).order_by('-total_sold')
    context['most_popular']  = product_sales.first()
    context['least_popular'] = product_sales.last()

    products_summary = Product.objects.annotate(
        total_qty=Coalesce(Sum('orderitem__quantity'), 0),
        total_revenue=Coalesce(
            Sum(F('orderitem__quantity') * F('orderitem__price_at_purchase')),
            Decimal('0'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).order_by('name')
    context['products_summary'] = products_summary
    context['total_all_revenue'] = sum(float(p.total_revenue) for p in products_summary)
    context['total_all_qty']     = sum(p.total_qty for p in products_summary)

    monthly_sales = list(
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
    context['monthly_sales'] = monthly_sales

    months_labels = [m['month'].strftime('%b %Y') for m in monthly_sales if m['month']]
    sales_data    = [float(m['total']) for m in monthly_sales]
    context['annual_revenue'] = round(sum(sales_data), 2)

    profitable_cats = list(
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

    buyers = CustomUser.objects.filter(role='buyer', birth_date__isnull=False)
    today  = date.today()
    ages   = [
        today.year - b.birth_date.year - ((today.month, today.day) < (b.birth_date.month, b.birth_date.day))
        for b in buyers
    ]
    if ages:
        context['mean_age']   = round(statistics.mean(ages), 1)
        context['median_age'] = statistics.median(ages)
    else:
        context['mean_age'] = context['median_age'] = 'Нет данных'

    trend_data = []
    forecast   = 0
    if len(sales_data) > 1:
        x = np.arange(len(sales_data))
        y = np.array(sales_data)
        k, b = np.polyfit(x, y, 1)
        trend_data = [round(float(k * xi + b), 2) for xi in x]
        forecast   = round(float(k * len(sales_data) + b), 2)
    context['forecast'] = max(forecast, 0)

    # =================================================================
    # СОЗДАНИЕ ГРАФИКОВ MATPLOTLIB
    # =================================================================

    # 1. График: Продажи по месяцам и тренд
    plt.figure(figsize=(8, 4))
    if months_labels:
        plt.plot(months_labels, sales_data, marker='o', color='blue', label='Реальные продажи')
        if trend_data:
            plt.plot(months_labels, trend_data, linestyle='--', color='red', label='Линейный тренд')
        plt.legend()
    else:
        plt.text(0.5, 0.5, 'Нет данных', ha='center')
    context['chart_sales'] = get_graph()

    # 2. Круговая диаграмма: Выручка по категориям
    plt.figure(figsize=(6, 6))
    cat_labels = [c.name for c in profitable_cats]
    cat_revenue = [float(c.revenue) for c in profitable_cats]
    if sum(cat_revenue) > 0:
        plt.pie(cat_revenue, labels=cat_labels, autopct='%1.1f%%', startangle=140)
    else:
        plt.text(0.5, 0.5, 'Нет данных', ha='center')
    context['chart_categories'] = get_graph()

    # 3. Столбчатая диаграмма: Клиенты по городам
    plt.figure(figsize=(8, 4))
    city_labels = [item['city'] if item['city'] else 'Не указан' for item in clients_by_city]
    city_data = [item['count'] for item in clients_by_city]
    if city_labels:
        plt.bar(city_labels, city_data, color='gray')
    else:
        plt.text(0.5, 0.5, 'Нет данных', ha='center')
    context['chart_cities'] = get_graph()

    return render(request, 'orders/admin_dashboard.html', context)
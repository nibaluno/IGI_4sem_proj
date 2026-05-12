from django.urls import path, re_path
from . import views

urlpatterns = [
    # Промокоды и их CRUD
    path('promocodes/', views.promocode_list_view, name='promocodes'),
    path('promocodes/create/', views.promocode_create, name='promocode_create'),
    path('promocodes/edit/<int:id>/', views.promocode_edit, name='promocode_edit'),
    path('promocodes/delete/<int:id>/', views.promocode_delete, name='promocode_delete'),
    
    path('cart/', views.cart_view, name='cart'),
    
    # Регулярка для ID заказа
    re_path(r'^order/(?P<pk>[0-9]+)/$', views.order_detail_view, name='order_detail'),
    
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
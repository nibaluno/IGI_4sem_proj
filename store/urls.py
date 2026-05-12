from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('reviews/', views.all_reviews_view, name='all_reviews'),
    
    # CRUD для товаров
    path('create/', views.product_create, name='product_create'),
    path('edit/<int:id>/', views.product_edit, name='product_edit'),
    path('delete/<int:id>/', views.product_delete, name='product_delete'),
    
    # Отзывы
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    
    # Регулярное выражение для PK (Фаза 4)
    re_path(r'^(?P<pk>[0-9]+)/$', views.product_detail_view, name='product_detail'),
]
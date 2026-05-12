from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'), 
    path('about/', views.about_view, name='about'),
    
    # Регулярки для новостей
    path('news/', views.news_list_view, name='news_list'),
    re_path(r'^news/(?P<year>[0-9]{4})/(?P<slug>[-\w]+)/$', views.news_detail_view, name='news_detail'),
    
    # CRUD Словаря
    path('glossary/', views.glossary_index, name='glossary'),
    path('glossary/create/', views.glossary_create, name='glossary_create'),
    path('glossary/edit/<int:id>/', views.glossary_edit, name='glossary_edit'),
    path('glossary/delete/<int:id>/', views.glossary_delete, name='glossary_delete'),

    # Инфо-страницы
    path('contacts/', views.contacts_view, name='contacts'),
    path('vacancies/', views.vacancies_view, name='vacancies'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('reviews/', views.reviews_view, name='reviews_info'),
]
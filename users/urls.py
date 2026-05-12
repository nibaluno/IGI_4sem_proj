from django.urls import path, re_path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # CRUD (Read) для сотрудников
    path('clients/', views.client_list_view, name='client_list'),
    
    # Использование регулярного выражения для ID пользователя
    re_path(r'^clients/(?P<pk>[0-9]+)/$', views.client_detail_view, name='client_detail'),
]
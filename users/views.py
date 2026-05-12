from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import CustomUser
from .forms import CustomUserCreationForm
from services.api_services import get_cat_fact, get_random_joke

# 1. Регистрация (Create)
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# 2. Вход (Login)
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# 3. Выход (Logout)
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('home')

# 4. Личный кабинет (Read)
@login_required
def profile_view(request):
    # Вызываем API 
    cat_fact = get_cat_fact()
    random_joke = get_random_joke()
    return render(request, 'users/profile.html', {
        'cat_fact': cat_fact,
        'random_joke': random_joke
    })

# 5. Список клиентов для сотрудников (Read)
@login_required
def client_list_view(request):
    # Ручная проверка роли вместо миксина
    if request.user.role != 'employee' and not request.user.is_superuser:
        return HttpResponseForbidden("Доступ запрещен. Только для сотрудников.")
    
    clients = CustomUser.objects.filter(role='buyer')
    return render(request, 'users/client_list.html', {'clients': clients})

# 6. Детальная информация о клиенте (Read)
@login_required
def client_detail_view(request, pk):
    # Ручная проверка роли
    if request.user.role != 'employee' and not request.user.is_superuser:
        return HttpResponseForbidden("Доступ запрещен. Только для сотрудников.")
    
    client_user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'users/client_detail.html', {'client_user': client_user})
import calendar
import zoneinfo
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.utils import timezone 

# ИМПОРТИРУЕМ МОДЕЛИ
from .models import News, CompanyInfo, GlossaryTerm, Contact, Vacancy, PrivacyPolicy
from store.models import Review

# ==========================================
# 1. ГЛАВНАЯ СТРАНИЦА (С календарем и часовым поясом)
# ==========================================
def home_view(request):
    latest_news = News.objects.order_by('-date_published').first()
    
    # Получаем время
    now_utc = timezone.now()
    
    # Получаем таймзону (если пользователь вошел - берем его, иначе Минск)
    tz_name = request.user.timezone if request.user.is_authenticated else 'Europe/Minsk'
    
    # Конвертируем время
    try:
        now_local = now_utc.astimezone(zoneinfo.ZoneInfo(tz_name))
    except:
        now_local = now_utc # Если часовой пояс не найден, выводим UTC
    
    # Создаем календарь
    cal = calendar.TextCalendar(firstweekday=0)
    month_cal = cal.formatmonth(now_local.year, now_local.month)
    
    return render(request, 'info/home.html', {
        'latest_news': latest_news,
        'now_utc': now_utc,
        'now_local': now_local,
        'month_cal': month_cal,
    })

# ==========================================
# 2. ИНФО-СТРАНИЦЫ (О компании, Контакты, Вакансии, Политика, Отзывы)
# ==========================================
def about_view(request):
    company = CompanyInfo.objects.first()
    return render(request, 'info/about.html', {'company': company})

def contacts_view(request):
    contacts = Contact.objects.all()
    return render(request, 'info/contacts.html', {'contacts': contacts})

def vacancies_view(request):
    # Берем только активные вакансии
    vacancies = Vacancy.objects.filter(is_active=True)
    return render(request, 'info/vacancies.html', {'vacancies': vacancies})

def privacy_view(request):
    policy = PrivacyPolicy.objects.first()
    return render(request, 'info/privacy.html', {'policy': policy})

def reviews_view(request):
    reviews = Review.objects.all()
    return render(request, 'info/reviews.html', {'reviews': reviews})

# ==========================================
# 3. НОВОСТИ (Список и детальная страница с регуляркой)
# ==========================================
def news_list_view(request):
    news_list = News.objects.all()
    return render(request, 'info/news_list.html', {'news_list': news_list})

def news_detail_view(request, year, slug):
    # Вытаскиваем новость по слагу и году (как требует регулярка в URL)
    news_item = get_object_or_404(News, slug=slug, date_published__year=year)
    
    # ИСПРАВЛЕНО: передаем в HTML под правильным именем 'news_item'
    return render(request, 'info/news_detail.html', {'news_item': news_item})

# ==========================================
# 4. СЛОВАРЬ ТЕРМИНОВ (ИДЕАЛЬНЫЙ РУЧНОЙ CRUD)
# ==========================================

# 1. Чтение и вывод (Read)
def glossary_index(request):
    terms = GlossaryTerm.objects.all()
    return render(request, "info/glossary.html", {"terms": terms})

# 2. Создание (Create)
def glossary_create(request):
    if request.method == "POST":
        term_obj = GlossaryTerm()
        # Достаем данные из POST-запроса вручную!
        term_obj.term = request.POST.get("term")
        term_obj.definition = request.POST.get("definition")
        term_obj.save()
    return HttpResponseRedirect("/glossary/")

# 3. Редактирование (Update)
def glossary_edit(request, id):
    try:
        term_obj = GlossaryTerm.objects.get(id=id)
        if request.method == "POST":
            term_obj.term = request.POST.get("term")
            term_obj.definition = request.POST.get("definition")
            term_obj.save()
            return HttpResponseRedirect("/glossary/")
        else:
            return render(request, "info/glossary_edit.html", {"term_obj": term_obj})
    except GlossaryTerm.DoesNotExist:
        return HttpResponseNotFound("<h2>Термин не найден</h2>")
     
# 4. Удаление (Delete)
def glossary_delete(request, id):
    try:
        term_obj = GlossaryTerm.objects.get(id=id)
        term_obj.delete()
        return HttpResponseRedirect("/glossary/")
    except GlossaryTerm.DoesNotExist:
        return HttpResponseNotFound("<h2>Термин не найден</h2>")
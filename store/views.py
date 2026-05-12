from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from .models import Product, Category, Manufacturer, Review

# 1. Список товаров (Read)
def product_list_view(request):
    products = Product.objects.all()
    
    # Поиск
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)
    
    # Сортировка
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
            
    return render(request, 'store/catalog.html', {'products': products})

# 2. Детальная страница товара (Read)
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

# 3. Создание товара (Create - CRUD на фронте)
def product_create(request):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ запрещен")
    
    if request.method == "POST":
        p = Product()
        p.name = request.POST.get("name")
        p.price = request.POST.get("price")
        p.stock = request.POST.get("stock")
        p.unit = request.POST.get("unit")
        p.category = Category.objects.get(id=request.POST.get("category"))
        p.manufacturer = Manufacturer.objects.get(id=request.POST.get("manufacturer"))
        # p.photo = request.FILES.get("photo") # Если нужно загружать фото
        p.save()
        return redirect('product_list')
    
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    return render(request, 'store/product_form.html', {
        'categories': categories, 
        'manufacturers': manufacturers
    })

# 4. Редактирование товара (Update - CRUD на фронте)
def product_edit(request, id):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ запрещен")
    
    product = get_object_or_404(Product, id=id)
    
    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.unit = request.POST.get("unit")
        product.save()
        return redirect('product_detail', pk=product.id)
    
    # Добавляем категории и производителей, чтобы форма не была пустой
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    
    return render(request, 'store/product_form.html', {
        'product': product,
        'categories': categories,
        'manufacturers': manufacturers
    })

# 5. Удаление товара (Delete - CRUD на фронте)
def product_delete(request, id):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ запрещен")
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('product_list')

# 6. Добавление отзыва (Ручной POST запрос)
def add_review(request, product_id):
    if request.method == "POST" and request.user.is_authenticated:
        r = Review()
        r.product = Product.objects.get(id=product_id)
        r.user = request.user
        r.text = request.POST.get("text")
        r.rating = request.POST.get("rating")
        r.save()
    return redirect('product_detail', pk=product_id)

# 7. Все отзывы
def all_reviews_view(request):
    reviews = Review.objects.all().order_by('-date_added')
    return render(request, 'store/reviews.html', {'reviews': reviews})
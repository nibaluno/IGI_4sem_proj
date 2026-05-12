from django import forms
from .models import Product, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'manufacturer', 'price', 'unit', 'stock', 'photo']
        widgets = {
            'name':  forms.TextInput(attrs={'placeholder': 'Название товара'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text':   forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ваш отзыв...'}),
            'rating': forms.Select(choices=[(i, f'{i} ★') for i in range(1, 6)]),
        }
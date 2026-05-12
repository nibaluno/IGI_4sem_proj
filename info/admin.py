from django.contrib import admin
from .models import *

class CompanyHistoryInline(admin.TabularInline):
    model = CompanyHistory
    extra = 1

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    inlines = [CompanyHistoryInline]
    # prepopulated_fields = {'slug': ('title',)}
    # list_display = ('title', 'date_published')

admin.site.register(News)
admin.site.register(Vacancy)
admin.site.register(Contact)
admin.site.register(GlossaryTerm)
admin.site.register(PrivacyPolicy)
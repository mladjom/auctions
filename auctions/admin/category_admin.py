# auctions/admin/category_admin.py
from django.contrib import admin
from .base_admin import BaseModelAdmin

class CategoryAdmin(BaseModelAdmin):
    list_display = ('title_sr', 'slug')
    search_fields = ('title_sr',)

# auctions/admin/executor_admin.py
from django.contrib import admin

class ExecutorAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    readonly_fields = ('slug',)
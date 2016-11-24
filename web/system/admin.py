# -*- coding: utf-8 -*-
from django.contrib import admin

from web.system.models import SystemProperty


@admin.register(SystemProperty)
class SystemPropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    search_fields = ['name', 'value']
    list_filter = ['name', 'value']
    ordering = ['name']

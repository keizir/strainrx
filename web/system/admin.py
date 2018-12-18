# -*- coding: utf-8 -*-
from django.contrib import admin

from web.system.models import SystemProperty, PermanentlyRemoved, TopPageMetaData


@admin.register(SystemProperty)
class SystemPropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    search_fields = ['name', 'value']
    list_filter = ['name', 'value']
    ordering = ['name']


@admin.register(PermanentlyRemoved)
class PermanentlyRemovedAdmin(admin.ModelAdmin):
    list_display = ('url', 'status', 'redirect_url')


@admin.register(TopPageMetaData)
class TopPageMetaDataAdmin(admin.ModelAdmin):
    list_display = ('path', 'meta_title', 'meta_keywords')

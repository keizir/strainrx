# -*- coding: utf-8 -*-
from django.contrib import admin

from web.businesses.models import Business, BusinessLocation


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    pass


@admin.register(BusinessLocation)
class BusinessLocationAdmin(admin.ModelAdmin):
    pass

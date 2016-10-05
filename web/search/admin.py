# -*- coding: utf-8 -*-
from django.contrib import admin

from web.search.models import Strain


@admin.register(Strain)
class StrainAdmin(admin.ModelAdmin):
    pass

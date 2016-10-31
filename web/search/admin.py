# -*- coding: utf-8 -*-
from django.contrib import admin

from web.search.models import *


@admin.register(Strain)
class StrainAdmin(admin.ModelAdmin):
    pass


@admin.register(StrainImage)
class StrainImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Effect)
class EffectAdmin(admin.ModelAdmin):
    pass


@admin.register(UserSearch)
class UserSearchAdmin(admin.ModelAdmin):
    pass

# -*- coding: utf-8 -*-
from django.contrib import admin

from web.search.models import *


@admin.register(Strain)
class StrainAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'variety']
    search_fields = ['name', 'category', 'variety']
    list_filter = ['name', 'category', 'variety']
    ordering = ['name']


@admin.register(StrainReview)
class StrainReviewAdmin(admin.ModelAdmin):
    list_display = ['strain', 'rating', 'review_approved', 'created_date', 'created_by',
                    'last_modified_date', 'last_modified_by']
    search_fields = ['strain', 'rating', 'review_approved', 'created_date', 'created_by',
                     'last_modified_date', 'last_modified_by']
    list_filter = ['strain', 'rating', 'review_approved', 'created_date', 'created_by',
                   'last_modified_date', 'last_modified_by']
    ordering = ['strain', '-created_date']
    readonly_fields = ['strain', 'rating', 'review', 'created_date', 'created_by',
                       'last_modified_date', 'last_modified_by']


@admin.register(StrainImage)
class StrainImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Effect)
class EffectAdmin(admin.ModelAdmin):
    pass


@admin.register(UserSearch)
class UserSearchAdmin(admin.ModelAdmin):
    pass

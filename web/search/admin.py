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


def get_client_ip(request):
    return request.META.get('X-Real-IP')


def remove_user_reviews(modeladmin, request, queryset):
    for review in queryset:
        review.removed_date = datetime.now()
        review.last_modified_ip = get_client_ip(request)
        review.last_modified_by = request.user
        review.last_modified_date = datetime.now()
        review.save()


remove_user_reviews.short_description = 'Soft delete selected user reviews'


@admin.register(UserStrainReview)
class UserStrainReviewAdmin(admin.ModelAdmin):
    list_display = ['strain', 'created_by', 'effect_type', 'status', 'created_date', 'removed_date']
    search_fields = ['strain__name', 'created_by__email', 'created_by__first_name', 'created_by__last_name',
                     'effect_type', 'status', 'created_date', 'removed_date']
    list_filter = ['strain', 'created_by', 'effect_type', 'status', 'created_date', 'removed_date']
    ordering = ['-created_date']
    readonly_fields = ['strain', 'effect_type', 'effects', 'status', 'removed_date', 'created_by', 'created_date',
                       'created_by_ip', 'last_modified_date', 'last_modified_by', 'last_modified_by_ip']
    actions = [remove_user_reviews]


@admin.register(StrainImage)
class StrainImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Effect)
class EffectAdmin(admin.ModelAdmin):
    pass


@admin.register(UserSearch)
class UserSearchAdmin(admin.ModelAdmin):
    pass

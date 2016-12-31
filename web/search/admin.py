# -*- coding: utf-8 -*-
from django.contrib import admin

from web.search.models import *


@admin.register(Strain)
class StrainAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'variety']
    search_fields = ['name', 'category', 'variety']
    list_filter = ['name', 'category', 'variety']
    ordering = ['name']


def approve_selected_ratings(modeladmin, request, queryset):
    for rating in queryset:
        rating.review_approved = True
        rating.last_modified_by = request.user
        rating.save()


approve_selected_ratings.short_description = 'Approve selected ratings'


@admin.register(StrainReview)
class StrainReviewAdmin(admin.ModelAdmin):
    list_display = ['strain', 'rating', 'review', 'review_approved', 'created_date', 'created_by']
    search_fields = ['strain__name', 'rating', 'review_approved', 'created_date',
                     'created_by__email', 'created_by__first_name', 'created_by__last_name']
    list_filter = ['rating', 'review_approved', 'created_date', 'last_modified_date']
    ordering = ['strain', '-created_date']
    readonly_fields = ['strain', 'rating', 'review', 'created_date', 'created_by',
                       'last_modified_date', 'last_modified_by']
    actions = [approve_selected_ratings]


def get_client_ip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        return request.META.get('HTTP_X_FORWARDED_FOR').split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        return request.META.get('HTTP_X_REAL_IP')
    else:
        return request.META.get('REMOTE_ADDR')


def remove_user_ratings(modeladmin, request, queryset):
    for review in queryset:
        review.removed_date = datetime.now()
        review.last_modified_ip = get_client_ip(request)
        review.last_modified_by = request.user
        review.last_modified_date = datetime.now()
        review.save()


remove_user_ratings.short_description = 'Soft delete selected user ratings'


@admin.register(StrainRating)
class StrainRatingAdmin(admin.ModelAdmin):
    list_display = ['strain', 'created_by', 'status', 'created_date', 'removed_date']
    search_fields = ['strain__name', 'created_by__email', 'created_by__first_name', 'created_by__last_name',
                     'status', 'created_date', 'removed_date']
    list_filter = ['strain', 'created_by', 'status', 'created_date', 'removed_date']
    ordering = ['-created_date']
    readonly_fields = ['strain', 'effects', 'effects_changed', 'benefits', 'benefits_changed',
                       'side_effects', 'side_effects_changed', 'status', 'removed_date', 'created_by', 'created_date',
                       'created_by_ip', 'last_modified_date', 'last_modified_by', 'last_modified_by_ip']
    actions = [remove_user_ratings]


def approve_strain_image(modeladmin, request, queryset):
    for image in queryset:
        image.is_approved = True
        image.save()


approve_strain_image.short_description = 'Approve Image'


@admin.register(StrainImage)
class StrainImageAdmin(admin.ModelAdmin):
    list_display = ['strain', 'created_by', 'is_approved', 'created_date', 'image']
    search_fields = ['strain__name', 'created_by__email', 'created_by__first_name', 'created_by__last_name',
                     'is_approved']
    list_filter = ['is_approved', 'created_date']
    ordering = ['-created_date']
    readonly_fields = ['strain', 'created_by', 'created_date', 'image']
    actions = [approve_strain_image]


@admin.register(Effect)
class EffectAdmin(admin.ModelAdmin):
    pass


@admin.register(UserSearch)
class UserSearchAdmin(admin.ModelAdmin):
    pass

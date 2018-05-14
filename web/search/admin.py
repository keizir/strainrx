# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.db import models
from django.contrib.admin import SimpleListFilter
from tinymce.widgets import TinyMCE

from web.businesses.es_service import BusinessLocationESService
from web.businesses.models import BusinessLocationMenuItem
from web.search.models import *


def activate_selected_strains(modeladmin, request, queryset):
    for strain in queryset:
        strain.removed_by = None
        strain.removed_date = None
        strain.save()


activate_selected_strains.short_description = 'Activate selected'


def deactivate_selected_strains(modeladmin, request, queryset):
    business_location_es_service = BusinessLocationESService()

    for strain in queryset:
        # Delete strain from locations menu
        if BusinessLocationMenuItem.objects.filter(strain=strain).exists():
            for mi in BusinessLocationMenuItem.objects.filter(strain=strain):
                business_location_es_service.delete_menu_item(mi)
                mi.removed_date = datetime.now()
                mi.save()

        # Delete strain itself
        strain.removed_by = request.user.id
        strain.removed_date = datetime.now()
        strain.save()


deactivate_selected_strains.short_description = 'Deactivate selected'


class StrainAdminForm(forms.ModelForm):
    class Meta:
        model = Strain
        fields = '__all__'
        exclude = ['internal_id', 'removed_by', 'removed_date']

    about = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}), required=False)
    common_name = forms.CharField(required=False)


class StrainRemovedFilter(SimpleListFilter):
    title = 'Removed'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ]

    def queryset(self, request, queryset):
        removed_value = self.value()

        if removed_value == 'inactive':
            return queryset.exclude(removed_date=None)
        elif removed_value == 'active':
            return queryset.filter(removed_date=None)

        return queryset.all()


class StrainImageInline(admin.TabularInline):
    extra = 0
    model = StrainImage


@admin.register(Strain)
class StrainAdmin(admin.ModelAdmin):
    form = StrainAdminForm
    inlines = (StrainImageInline,)
    list_display = ('name', 'category', 'variety', 'removed_date')
    search_fields = ('name', 'category', 'variety')
    list_filter = (StrainRemovedFilter, 'category', 'variety', 'name')
    ordering = ('name',)
    actions = (activate_selected_strains, deactivate_selected_strains)


def approve_selected_ratings(modeladmin, request, queryset):
    for rating in queryset:
        rating.review_approved = True
        rating.last_modified_by = request.user
        rating.save()


approve_selected_ratings.short_description = 'Approve selected ratings'


@admin.register(StrainReview)
class StrainReviewAdmin(admin.ModelAdmin):
    list_display = ['strain', 'rating', 'review_approved', 'created_date', 'created_by']
    search_fields = ['strain__name', 'rating', 'review_approved', 'created_date',
                     'created_by__email', 'created_by__first_name', 'created_by__last_name']
    list_filter = ['rating', 'review_approved', 'created_date', 'last_modified_date']
    ordering = ['-created_date']
    actions = [approve_selected_ratings]
    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea},
    }


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
    list_display = ['strain', 'created_by', 'is_approved', 'is_primary', 'created_date', 'image']
    search_fields = ['strain__name', 'created_by__email', 'created_by__first_name', 'created_by__last_name',
                     'is_approved']
    list_filter = ['is_approved', 'created_date']
    ordering = ['-created_date']
    readonly_fields = ['strain', 'created_by', 'created_date', 'image']
    actions = [approve_strain_image, 'delete_selected']


@admin.register(Effect)
class EffectAdmin(admin.ModelAdmin):
    pass


@admin.register(Flavor)
class FlavorAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'data_name', 'image']
    search_fields = ['display_name', 'data_name']
    ordering = ['display_name']
    readonly_fields = ['data_name']


@admin.register(UserSearch)
class UserSearchAdmin(admin.ModelAdmin):
    search_fields = ['user__email']

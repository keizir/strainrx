# -*- coding: utf-8 -*-
from django.contrib import admin

from web.businesses.api.services import BusinessLocationService
from web.businesses.models import Business, BusinessLocation, LocationReview


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    pass


def activate_selected_locations(modeladmin, request, queryset):
    for l in queryset:
        l.removed_by = None
        l.removed_date = None
        l.save()


activate_selected_locations.short_description = 'Activate selected'


def deactivate_selected_locations(modeladmin, request, queryset):
    service = BusinessLocationService()
    for l in queryset:
        service.remove_location(l.id, request.user.id)


deactivate_selected_locations.short_description = 'Deactivate selected'


@admin.register(BusinessLocation)
class BusinessLocationAdmin(admin.ModelAdmin):
    def get_actions(self, request):
        # Disable delete
        actions = super(BusinessLocationAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

    def get_queryset(self, request):
        objects_all = BusinessLocation.objects.all()
        return objects_all

    list_display = ['business', 'location_name', 'dispensary', 'delivery', 'removed_date', 'removed_by']
    readonly_fields = ['slug_name']
    ordering = ['location_name']
    actions = [activate_selected_locations, deactivate_selected_locations]


def approve_selected_ratings(modeladmin, request, queryset):
    for rating in queryset:
        rating.review_approved = True
        rating.last_modified_by = request.user
        rating.save()


approve_selected_ratings.short_description = 'Approve selected ratings'


@admin.register(LocationReview)
class LocationReviewAdmin(admin.ModelAdmin):
    list_display = ['location', 'rating', 'review', 'review_approved', 'created_date', 'created_by']
    search_fields = ['location__name', 'rating', 'review_approved', 'created_date',
                     'created_by__email', 'created_by__first_name', 'created_by__last_name']
    list_filter = ['rating', 'review_approved', 'created_date', 'last_modified_date']
    ordering = ['-created_date']
    readonly_fields = ['location', 'rating', 'review', 'created_date', 'created_by',
                       'last_modified_date', 'last_modified_by']
    actions = [approve_selected_ratings]

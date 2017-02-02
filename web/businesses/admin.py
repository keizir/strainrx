# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTimeWidget
from tinymce.widgets import TinyMCE

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


class BusinessLocationAdminForm(forms.ModelForm):
    class Meta:
        model = BusinessLocation
        fields = '__all__'

    about = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}))
    location_field = forms.CharField(max_length=255)

    mon_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    mon_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    tue_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    tue_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    wed_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    wed_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    thu_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    thu_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    fri_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    fri_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    sat_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    sat_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    sun_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    sun_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)

    def __init__(self, *args, **kwargs):
        super(BusinessLocationAdminForm, self).__init__(*args, **kwargs)

        self.fields['location_email'].required = True
        self.fields['phone'].required = True
        self.fields['location_field'].required = True


@admin.register(BusinessLocation)
class BusinessLocationAdmin(admin.ModelAdmin):
    change_form_template = 'admin/business/business_location_change_form.html'
    form = BusinessLocationAdminForm

    fieldsets = (
        ('Info',
         {'fields': ('business', 'location_name', 'manager_name', 'location_email', 'phone', 'ext', 'about',), }),
        ('Type',
         {'fields': ('dispensary', 'delivery', 'delivery_radius',), }),
        ('Location',
         {'fields': ('location_field', 'street1', 'city', 'state', 'zip_code', 'lat', 'lng', 'location_raw',), }),
        ('Working Hours',
         {'fields': ('mon_open', 'mon_close', 'tue_open', 'tue_close', 'wed_open', 'wed_close', 'thu_open', 'thu_close',
                     'fri_open', 'fri_close', 'sat_open', 'sat_close', 'sun_open', 'sun_close',), }),
    )

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
    readonly_fields = ['category', 'slug_name', 'primary', 'grow_house']
    search_fields = ['location_name']
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

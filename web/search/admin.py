# -*- coding: utf-8 -*-
from boto.s3.bucket import Bucket
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.conf import settings
from django.contrib import admin

from web.businesses.es_service import BusinessLocationESService
from web.businesses.models import BusinessLocationMenuItem
from web.search.es_service import SearchElasticService
from web.search.models import *
from web.search.strain_user_rating_es_service import StrainUserRatingESService


def delete_selected_strains(modeladmin, request, queryset):
    strain_es_service = StrainESService()
    user_rating_es_service = StrainUserRatingESService()
    business_location_es_service = BusinessLocationESService()
    search_elastic_service = SearchElasticService()

    for strain in queryset:
        # Delete images from S3 and from database
        if StrainImage.objects.filter(strain=strain).exists():
            for sim in StrainImage.objects.filter(strain=strain):
                if sim.image and sim.image.url:
                    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                    bucket = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
                    k = Key(bucket=bucket, name=sim.image.url.split(bucket.name)[1])
                    k.delete()

                sim.delete()

        # Delete strain reviews
        if StrainReview.objects.filter(strain=strain).exists():
            for sr in StrainReview.objects.filter(strain=strain):
                strain_es_service.delete_strain_review_by_db_id(sr.id, strain.id)
                sr.delete()

        # Delete strain ratings
        if StrainRating.objects.filter(strain=strain).exists():
            for sr in StrainRating.objects.filter(strain=strain):
                user_rating_es_service.delete_user_review(strain.id, sr.created_by.id)
                sr.delete()

        # Delete strain from user favorites
        if UserFavoriteStrain.objects.filter(strain=strain).exists():
            for ufs in UserFavoriteStrain.objects.filter(strain=strain):
                ufs.delete()

        # Delete strain from locations menu
        if BusinessLocationMenuItem.objects.filter(strain=strain).exists():
            for mi in BusinessLocationMenuItem.objects.filter(strain=strain):
                business_location_es_service.delete_menu_item(mi.id, mi.business_location.id)
                mi.delete()

        # Delete strain itself and name from suggester
        search_elastic_service.delete_lookup_strain_name(strain.id)
        strain_es_service.delete_strain(strain.id)
        strain.delete()


delete_selected_strains.short_description = 'Delete selected (including relationships)'


@admin.register(Strain)
class StrainAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'variety']
    search_fields = ['name', 'category', 'variety']
    list_filter = ['name', 'category', 'variety']
    ordering = ['name']
    actions = [delete_selected_strains]


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

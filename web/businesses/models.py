from __future__ import unicode_literals, absolute_import

import re
from uuid import uuid4

import pytz
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from web.businesses.es_serializers import BusinessLocationESSerializer, MenuItemESSerializer
from web.businesses.es_service import BusinessLocationESService
from web.search.models import Strain
from web.users.models import User


def upload_business_image_to(instance, filename):
    path = 'businesses/{0}/images/{1}___{2}'.format(instance.pk, uuid4(), filename)
    return path


def upload_business_location_image_to(instance, filename):
    path = 'businesses/{0}/locations/{1}/images/{2}___{3}'.format(instance.business.pk, instance.pk, uuid4(), filename)
    return path


def validate_business_image(field_file_obj):
    file_size = field_file_obj.file.size
    megabyte_limit = settings.MAX_BUSINESS_IMAGE_SIZE
    if file_size > megabyte_limit:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


def phone_number_validator(value):
    phone_regex = re.compile('[0-9]{3}-[0-9]{3}-[0-9]{4}')
    if not phone_regex.match(value):
        raise ValidationError('Phone number must match the following format: 000-000-0000')


@python_2_unicode_compatible
class Business(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(max_length=255, upload_to=upload_business_image_to, blank=True,
                              help_text='Maximum file size allowed is 5Mb',
                              validators=[validate_business_image])

    certified_legal_compliance = models.BooleanField(default=False)
    users = models.ManyToManyField(User, related_name='businesses')

    # User who created the Business. Also included in [users] field
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='business_created_by')
    created_date = models.DateTimeField(auto_now_add=True)
    trial_period_start_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class BusinessLocation(models.Model):
    CATEGORY_CHOICES = (
        ('dispensary', 'Dispensary'),
        ('delivery', 'Delivery'),
    )

    business = models.ForeignKey(Business, on_delete=models.DO_NOTHING)
    location_name = models.CharField(max_length=255, blank=False, null=False)
    manager_name = models.CharField(max_length=255, blank=True, null=True)
    location_email = models.CharField(max_length=255, blank=True, null=True)

    image = models.ImageField(max_length=255, upload_to=upload_business_location_image_to, blank=True,
                              help_text='Maximum file size allowed is 5Mb',
                              validators=[validate_business_image])

    category = models.CharField(max_length=20, default='dispensary', choices=CATEGORY_CHOICES,
                                help_text='Warning: changing the category will change the URL of this location')

    slug_name = models.SlugField(max_length=611, null=True, blank=True,
                                 help_text='This will be automatically generated from a location name when created')

    primary = models.BooleanField(default=False)
    dispensary = models.BooleanField(default=False)
    delivery = models.BooleanField(default=False)
    grow_house = models.BooleanField(default=False)

    delivery_radius = models.FloatField(max_length=10, blank=True, null=True)

    street1 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    timezone = models.CharField(max_length=100, null=True, choices=zip(pytz.common_timezones, pytz.common_timezones))

    about = models.TextField(blank=True, null=True, default='')

    lat = models.FloatField(_('Latitude'), blank=True, null=True, max_length=50)
    lng = models.FloatField(_('Longitude'), blank=True, null=True, max_length=50)
    location_raw = JSONField(_('Location Raw JSON'), default={}, blank=True, null=True, max_length=20000)

    phone = models.CharField(max_length=15, blank=True, null=True, validators=[phone_number_validator])
    ext = models.CharField(max_length=5, blank=True, null=True)

    removed_by = models.CharField(max_length=20, blank=True, null=True)
    removed_date = models.DateTimeField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)

    mon_open = models.TimeField(blank=True, null=True)
    mon_close = models.TimeField(blank=True, null=True)
    tue_open = models.TimeField(blank=True, null=True)
    tue_close = models.TimeField(blank=True, null=True)
    wed_open = models.TimeField(blank=True, null=True)
    wed_close = models.TimeField(blank=True, null=True)
    thu_open = models.TimeField(blank=True, null=True)
    thu_close = models.TimeField(blank=True, null=True)
    fri_open = models.TimeField(blank=True, null=True)
    fri_close = models.TimeField(blank=True, null=True)
    sat_open = models.TimeField(blank=True, null=True)
    sat_close = models.TimeField(blank=True, null=True)
    sun_open = models.TimeField(blank=True, null=True)
    sun_close = models.TimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is None and not self.slug_name:
            # determine a category
            self.category = 'dispensary' if self.dispensary else 'delivery' if self.delivery else 'dispensary'

            # create a slug name
            slugified_name = slugify('{0} {1}'.format(self.location_name, self.city))
            if not exist_by_slug_name(slugified_name):
                self.slug_name = slugified_name
            else:
                for x in range(1, 1000):
                    new_slug_name = '{0}-{1}'.format(slugified_name, x)
                    if not exist_by_slug_name(new_slug_name):
                        self.slug_name = new_slug_name
                        break

        super(BusinessLocation, self).save(*args, **kwargs)

    def clean(self):
        delivery = self.delivery
        dispensary = self.dispensary

        if not delivery and not dispensary:
            raise ValidationError('Either delivery or dispensary is required.')

    def get_absolute_url(self):
        return reverse('businesses:dispensary_info',
                       kwargs={'location_category': self.category, 'location_slug': self.slug_name})

    def __str__(self):
        return self.location_name


def exist_by_slug_name(location_slug_name):
    return BusinessLocation.objects.filter(slug_name=location_slug_name).exists()


@receiver(post_save, sender=BusinessLocation)
def save_es_business_location(sender, **kwargs):
    business_location = kwargs.get('instance')
    es_serializer = BusinessLocationESSerializer(business_location)
    data = es_serializer.data
    data['business_id'] = business_location.business.pk
    data['business_location_id'] = business_location.pk
    data['removed_by_id'] = business_location.removed_by
    data['slug_name'] = business_location.slug_name
    BusinessLocationESService().save_business_location(data, business_location.pk)


@python_2_unicode_compatible
class BusinessLocationMenuItem(models.Model):
    business_location = models.ForeignKey(BusinessLocation, on_delete=models.DO_NOTHING)
    strain = models.ForeignKey(Strain, on_delete=models.DO_NOTHING)

    price_gram = models.FloatField(max_length=50, blank=True, null=True)
    price_eighth = models.FloatField(max_length=50, blank=True, null=True)
    price_quarter = models.FloatField(max_length=50, blank=True, null=True)
    price_half = models.FloatField(max_length=50, blank=True, null=True)

    in_stock = models.BooleanField(default=True)

    removed_date = models.DateTimeField(blank=True, null=True)


@receiver(post_save, sender=BusinessLocationMenuItem)
def save_es_menu_item(sender, **kwargs):
    menu_item = kwargs.get('instance')
    es_serializer = MenuItemESSerializer(menu_item)
    d = es_serializer.data

    strain = menu_item.strain
    d['id'] = menu_item.pk
    d['strain_id'] = strain.pk
    d['strain_name'] = strain.name
    BusinessLocationESService().save_menu_item(d, menu_item.pk, menu_item.business_location.pk)


@python_2_unicode_compatible
class UserFavoriteLocation(models.Model):
    location = models.ForeignKey(BusinessLocation, on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now=True)


@python_2_unicode_compatible
class LocationReview(models.Model):
    location = models.ForeignKey(BusinessLocation, on_delete=models.DO_NOTHING)

    rating = models.FloatField()
    review = models.CharField(max_length=500, default='', blank=True)
    review_approved = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='+')
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='+')

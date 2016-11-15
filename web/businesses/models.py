from __future__ import unicode_literals, absolute_import

import re
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from web.search.models import Strain
from web.users.models import User


def upload_business_image_to(instance, filename):
    path = 'businesses/{0}/images/{1}___{2}'.format(instance.pk, uuid4(), filename)
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
    business = models.ForeignKey(Business, on_delete=models.DO_NOTHING)
    location_name = models.CharField(max_length=255, blank=True, null=True)
    manager_name = models.CharField(max_length=255, blank=True, null=True)
    location_email = models.CharField(max_length=255, blank=True, null=True)

    primary = models.BooleanField(default=False)
    dispensary = models.BooleanField(default=False)
    delivery = models.BooleanField(default=False)
    grow_house = models.BooleanField(default=False)

    delivery_radius = models.FloatField(max_length=10, blank=True, null=True)

    street1 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

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

    def __str__(self):
        return '{0} - {1}'.format(self.business, self.location_name)


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

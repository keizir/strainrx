from __future__ import unicode_literals, absolute_import

import re
from uuid import uuid4

import pytz
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from web.businesses.es_serializers import BusinessLocationESSerializer, MenuItemESSerializer
from web.businesses.es_service import BusinessLocationESService
from web.search.models import Strain
from web.users.models import User
from django.conf import settings
from django_resized import ResizedImageField

@python_2_unicode_compatible
class State(models.Model):
    abbreviation = models.CharField(max_length=2, blank=False, null=False, db_index=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True,
                                   help_text='This will be used on /dispensaries page as a state description')
    description2 = models.TextField(blank=True, null=True,
                                    help_text='This will be used on /dispensaries/{state} page as a state description')
    active = models.BooleanField(default=True, help_text='Display this state on the dispensaries list page?')

    def get_absolute_url(self):
        return reverse('businesses:dispensaries_state_list', kwargs={'state': self.abbreviation.lower()})

    def __str__(self):
        return self.abbreviation


@python_2_unicode_compatible
class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    full_name_slug = models.SlugField(max_length=150, null=True, blank=True, db_index=True,
                                      help_text='This will be automatically changed from a city full name when updated')
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.full_name_slug = slugify(self.full_name)
        super(City, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('businesses:dispensaries_city_list',
                       kwargs={'state': self.state.abbreviation.lower(), 'city_slug': self.full_name_slug})

    def __str__(self):
        return self.full_name


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
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

def upload_to(instance, filename):
    path = 'articles/{0}_{1}'.format(uuid4(), filename)
    return path

@python_2_unicode_compatible
class BusinessLocation(models.Model):
    class Meta:
        unique_together = (("state_fk", "city_fk", "slug_name"),)

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

    category = models.CharField(max_length=20, default='dispensary', choices=CATEGORY_CHOICES)

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

    city_slug = models.SlugField(max_length=611, null=True, blank=True,
                                 help_text='This will be automatically generated from a city when updated')

    state_fk = models.ForeignKey(State, on_delete=models.DO_NOTHING, null=True)
    city_fk = models.ForeignKey(City, on_delete=models.DO_NOTHING, null=True)

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

    # social fields
    meta_desc = models.CharField(max_length=3072, blank=True)
    meta_keywords = models.CharField(max_length=3072, blank=True)

    def validate_image(field_file_obj):
        file_size = field_file_obj.file.size
        megabyte_limit = settings.MAX_IMAGE_SIZE
        if file_size > megabyte_limit:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    social_image = ResizedImageField(max_length=255, blank=True, help_text='Maximum file size allowed is 10Mb', validators=[validate_image], quality=75, size=[1024, 1024], upload_to=upload_to)

    def image_url(self):
        # helper to get image url or return default
        if self.image and hasattr(self.image, 'url') and self.image.url:
            return self.image.url
        else:
            return None

    def save(self, *args, **kwargs):
        if self.pk is None and not self.slug_name:
            # determine a category
            self.category = 'dispensary' if self.dispensary else 'delivery' if self.delivery else 'dispensary'

            # create a slug name
            slugified_name = slugify(self.location_name)
            slugified_name_and_street = '{0}-{1}'.format(slugify(self.location_name), slugify(self.street1))
            if not exist_by_slug_name(slugified_name):
                self.slug_name = slugified_name
            elif not exist_by_slug_name(slugified_name_and_street):
                self.slug_name = slugified_name_and_street
            else:
                for x in range(1, 1000):
                    new_slug_name = '{0}-{1}'.format(slugified_name_and_street, x)
                    if not exist_by_slug_name(new_slug_name):
                        self.slug_name = new_slug_name
                        break

        if self.city:
            self.city_slug = slugify(self.city)

        super(BusinessLocation, self).save(*args, **kwargs)

    def clean(self):
        delivery = self.delivery
        dispensary = self.dispensary

        if not delivery and not dispensary:
            raise ValidationError('Either delivery or dispensary is required.')

    def get_absolute_url(self):
        return reverse('businesses:dispensary_info',
                       kwargs={'state': self.state_fk.abbreviation.lower(), 'city_slug': self.city_fk.full_name_slug,
                               'slug_name': self.slug_name})

    def __str__(self):
        return self.location_name


def exist_by_slug_name(location_slug_name):
    return BusinessLocation.objects.filter(slug_name=location_slug_name).exists()


@receiver(pre_save, sender=BusinessLocation)
def pre_save_business_location(sender, **kwargs):
    business_location = kwargs.get('instance')
    save_city_and_state(business_location)


@receiver(post_save, sender=BusinessLocation)
def post_save_business_location(sender, **kwargs):
    business_location = kwargs.get('instance')
    es_serializer = BusinessLocationESSerializer(business_location)
    data = es_serializer.data
    data['business_id'] = business_location.business.pk
    data['business_location_id'] = business_location.pk
    data['removed_by_id'] = business_location.removed_by
    data['slug_name'] = business_location.slug_name
    data['url'] = business_location.get_absolute_url()
    data['image'] = business_location.image_url()
    BusinessLocationESService().save_business_location(data, business_location.pk)


def save_city_and_state(business_location):
    state = business_location.state
    city = business_location.city

    if state and not State.objects.filter(abbreviation__iexact=state.lower()).exists():
        s = State(abbreviation=state.upper())
        s.save()
    else:
        s = State.objects.get(abbreviation__iexact=state.lower())

    if city and not City.objects.filter(state=s, full_name__iexact=city.lower()).exists():
        c = City(state=s, full_name=city)
        c.save()
    else:
        c = City.objects.get(state=s, full_name__iexact=city.lower())

    business_location.state_fk = s
    business_location.city_fk = c


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

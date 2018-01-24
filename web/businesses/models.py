from __future__ import unicode_literals, absolute_import

from datetime import datetime
import re
from uuid import uuid4

import pytz
from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db.models import PointField, GeoManager
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.query import Q
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from web.businesses.emails import EmailService
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
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, related_name='cities')
    full_name = models.CharField(max_length=100, blank=True, null=True)
    full_name_slug = models.SlugField(max_length=150, null=True, blank=True, db_index=True,
                                      help_text='This will be automatically changed from a city full name when updated')
    description = models.TextField(blank=True, null=True)

    SEO_FRIENDLY_DESCRIPTION_TEMPLATE = """
        Find marijuana {location_type} in the city of {city}, {state}.
        Get the strains ideally suited for your individual needs,
        browse the best deals and the closest vendors to get the most convenience and value.
        """

    def seo_friendly_description(self, location_type=''):
        if self.description:
            return self.description

        try:
            state = self.state.full_name or self.state.abbreviation
        except Exception:
            state = 'US'

        return self.SEO_FRIENDLY_DESCRIPTION_TEMPLATE.format(city=self.full_name, state=state,
                                                             location_type=location_type)

    @property
    def seo_friendly_dispensaries_description(self):
        return self.seo_friendly_description(location_type='dispensaries')

    @property
    def seo_friendly_growers_description(self):
        return self.seo_friendly_description(location_type='growers')

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
    ACCOUNT_TYPE_CHOICES = (
        ('house_account', 'House Account'),
        ('claimed_account_free', 'Claimed Account Free'),
        ('paid_account', 'Paid Account'),
    )

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

    account_type = models.CharField(max_length=255, choices=ACCOUNT_TYPE_CHOICES, default=ACCOUNT_TYPE_CHOICES[0][0])
    last_payment_date = models.DateField(null=True)
    last_payment_amount = models.PositiveIntegerField(null=True)

    is_searchable = models.BooleanField(default=True)

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
        ('grow_house', 'Grow House'),
    )

    DEFAULT_IMAGE_URL = '{base}images/default-location-image.jpeg'.format(base=settings.STATIC_URL)

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
    grow_details = JSONField(default={'organic': False,
                                      'pesticide_free': False,
                                      'indoor': False},
                             blank=True, null=True)

    street1 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10, db_index=True)
    timezone = models.CharField(max_length=100, null=True, choices=zip(pytz.common_timezones, pytz.common_timezones))

    city_slug = models.SlugField(max_length=611, null=True, blank=True,
                                 help_text='This will be automatically generated from a city when updated')

    state_fk = models.ForeignKey(State, on_delete=models.DO_NOTHING, null=True, related_name='business_locations')
    city_fk = models.ForeignKey(City, on_delete=models.DO_NOTHING, null=True, related_name='business_locations')

    about = models.TextField(blank=True, null=True, default='')

    lat = models.FloatField(_('Latitude'), blank=True, null=True, max_length=50)
    lng = models.FloatField(_('Longitude'), blank=True, null=True, max_length=50)
    location_raw = JSONField(_('Location Raw JSON'), default={}, blank=True, null=True, max_length=20000)
    geo_location = PointField(geography=True, srid=4326, null=True, db_index=True)

    phone = models.CharField(max_length=15, blank=True, null=True, validators=[phone_number_validator])
    ext = models.CharField(max_length=5, blank=True, null=True)

    verified = models.BooleanField(default=False)
    removed_by = models.CharField(max_length=20, blank=True, null=True)
    removed_date = models.DateTimeField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    menu_updated_date = models.DateField(null=True)

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

    objects = GeoManager()

    def validate_image(field_file_obj):
        file_size = field_file_obj.file.size
        megabyte_limit = settings.MAX_IMAGE_SIZE
        if file_size > megabyte_limit:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    social_image = ResizedImageField(max_length=255, blank=True, help_text='Maximum file size allowed is 10Mb', validators=[validate_image], quality=75, size=[1024, 1024], upload_to=upload_to)

    @property
    def url(self):
        return reverse('businesses:dispensary_info',
                       kwargs={'state': self.state_fk.abbreviation.lower(), 'city_slug': self.city_fk.full_name_slug,
                               'slug_name': self.slug_name})

    @property
    def urls(self):
        urls = {}
        kwargs = {
            'state': self.state_fk.abbreviation.lower(),
            'city_slug': self.city_fk.full_name_slug,
            'slug_name': self.slug_name,
        }

        if self.dispensary:
            urls['dispensary'] = reverse('businesses:dispensary_info', kwargs=kwargs)

        if self.grow_house:
            urls['grow_house'] = reverse('businesses:grower_info', kwargs=kwargs)

        return urls

    @property
    def image_url(self):
        # helper to get image url or return default
        if self.image and hasattr(self.image, 'url') and self.image.url:
            return self.image.url
        else:
            return self.DEFAULT_IMAGE_URL

    @property
    def about_or_default(self):
        if self.about:
            return self.about

        types = []
        if self.dispensary:
            types.append('dispensary')
        if self.grow_house:
            types.append('grow house')
        if self.delivery:
            types.append('delivery')

        if len(types) == 0:
            combined_type = 'business'
        elif len(types) == 1:
            combined_type = types[0]
        elif len(types) == 2:
            combined_type = ' and '.join(types)
        else:
            combined_type = ', '.join(types[:-1]) + ' and ' + types[-1]

        template = '{name} is a Marijuana {combined_type} located in {city}, {state}'
        context = {
            'name': self.location_name,
            'combined_type': combined_type,
            'city': self.city,
            'state': self.state,
        }

        return template.format(**context)

    @property
    def formatted_address(self):
        return ', '.join((self.street1, self.city, self.zip_code, self.state))

    @property
    def days_since_menu_update(self):
        if not self.menu_updated_date:
            return -1

        return (self.get_current_datetime().date() - self.menu_updated_date).days

    def get_current_datetime(self):
        if not self.timezone:
            timezone = 'UTC'
        else:
            timezone = self.timezone

        return datetime.now(pytz.timezone(timezone))

    def is_searchable(self):
        if self.removed_by or self.removed_date:
            return False

        return self.business.is_searchable

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

        self.geo_location = Point(self.lng, self.lat)

        super(BusinessLocation, self).save(*args, **kwargs)

    def clean(self):
        if not any((self.delivery, self.dispensary, self.grow_house)):
            raise ValidationError('Business Location needs to be one of the '
                                  'following: delivery, dispensary or grow house.')

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
    BusinessLocationESService().save_business_location(business_location)


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
    strain = models.ForeignKey(Strain, on_delete=models.DO_NOTHING, related_name='menu_items')

    price_gram = models.FloatField(max_length=50, blank=True, null=True)
    price_eighth = models.FloatField(max_length=50, blank=True, null=True)
    price_quarter = models.FloatField(max_length=50, blank=True, null=True)
    price_half = models.FloatField(max_length=50, blank=True, null=True)

    in_stock = models.BooleanField(default=True)

    removed_date = models.DateTimeField(blank=True, null=True)


@python_2_unicode_compatible
class BusinessLocationMenuUpdate(models.Model):
    business_location = models.ForeignKey(BusinessLocation, related_name='menu_updates')
    date = models.DateField()

    @classmethod
    def record_business_location_menu_update(cls, business_location):
        update_date = business_location.get_current_datetime().date()

        cls.objects.get_or_create(business_location=business_location, date=update_date)

        to_update = BusinessLocation.objects.filter(id=business_location.id)
        to_update = to_update.filter(
            Q(menu_updated_date__lt=update_date) |
            Q(menu_updated_date__isnull=True),
        )
        to_update.update(menu_updated_date=update_date)


@receiver(post_save, sender=BusinessLocationMenuItem)
def save_es_menu_item(sender, **kwargs):
    menu_item = kwargs.get('instance')

    BusinessLocationESService().save_menu_item(menu_item)
    BusinessLocationMenuUpdate.record_business_location_menu_update(menu_item.business_location)

    unserved_requests = BusinessLocationMenuUpdateRequest.objects.filter(
        business_location=menu_item.business_location,
        served=False,
    )
    unserved_requests = unserved_requests.select_related('user', 'business_location')

    email_service = EmailService()
    for request in unserved_requests:
        if request.send_notification:
            email_service.send_menu_update_request_served_email(request)

        request.served = True
        request.save()


@python_2_unicode_compatible
class BusinessLocationMenuUpdateRequest(models.Model):
    user = models.ForeignKey(User)
    business_location = models.ForeignKey(BusinessLocation)
    message = models.TextField(null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    send_notification = models.BooleanField(default=False)
    served = models.BooleanField(default=False)


@python_2_unicode_compatible
class GrowerDispensaryPartnership(models.Model):
    grower = models.ForeignKey(BusinessLocation, related_name='dispensary_partnerships')
    dispensary = models.ForeignKey(BusinessLocation, related_name='grower_partnerships')


@python_2_unicode_compatible
class FeaturedBusinessLocation(models.Model):
    class Meta:
        unique_together = (('business_location', 'zip_code'),)

    featured_datetime = models.DateTimeField(auto_now=True)
    business_location = models.ForeignKey(BusinessLocation, related_name='featured')
    zip_code = models.CharField(max_length=10, db_index=True)


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


@python_2_unicode_compatible
class Payment(models.Model):
    amount = models.PositiveIntegerField()
    business = models.ForeignKey(Business, on_delete=models.DO_NOTHING, related_name='payments')
    date = models.DateField()
    description = models.TextField(default='', blank=True)


def update_business_payments(business_id):
    amount, date = None, None

    last_payment = Payment.objects.filter(business_id=business_id).order_by('date').last()

    if last_payment is not None:
        amount = last_payment.amount
        date = last_payment.date

    Business.objects.filter(id=business_id).update(last_payment_amount=amount,
                                                   last_payment_date=date)


@receiver(post_save, sender=Payment)
def post_save_payment(sender, **kwargs):
    payment = kwargs.get('instance')
    update_business_payments(payment.business_id)


@receiver(post_delete, sender=Payment)
def post_delete_payment(sender, **kwargs):
    payment = kwargs.get('instance')
    update_business_payments(payment.business_id)

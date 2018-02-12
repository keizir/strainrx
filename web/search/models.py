from __future__ import unicode_literals, absolute_import
from django.conf import settings
from datetime import datetime
from json import loads, dumps
from uuid import uuid4

from django.contrib.postgres.fields import JSONField
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from web.search.serializers import StrainReviewESSerializer
from web.search.strain_es_service import StrainESService
from web.users.models import User
from django_resized import ResizedImageField


def upload_to(instance, filename):
    path = 'articles/{0}_{1}'.format(uuid4(), filename)
    return path


@python_2_unicode_compatible
class Strain(models.Model):
    class Meta:
        unique_together = (("name", "category"),)

    VARIETY_CHOICES = (
        ('sativa', 'Sativa'),
        ('indica', 'Indica'),
        ('hybrid', 'Hybrid'),
    )

    CATEGORY_CHOICES = (
        ('flower', 'Flower'),
        ('edible', 'Edible'),
        ('liquid', 'Liquid'),
        ('oil', 'Oil'),
        ('wax', 'Wax'),
    )

    internal_id = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255, null=True)
    strain_slug = models.SlugField(max_length=611, null=True, blank=True,
                                   help_text='Warning: changing the slug will change the URL of this strain')

    variety = models.CharField(max_length=255, choices=VARIETY_CHOICES)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)

    effects = JSONField(default={"happy": 0, "uplifted": 0, "stimulated": 0, "energetic": 0,
                                 "creative": 0, "focused": 0, "relaxed": 0, "sleepy": 0, "talkative": 0,
                                 "euphoric": 0, "hungry": 0, "tingly": 0, "good_humored": 0})

    benefits = JSONField(default={"reduce_stress": 0, "help_depression": 0, "relieve_pain": 0, "reduce_fatigue": 0,
                                  "reduce_headaches": 0, "help_muscles_spasms": 0, "lower_eye_pressure": 0,
                                  "reduce_nausea": 0, "reduce_inflammation": 0, "relieve_cramps": 0,
                                  "help_with_seizures": 0, "restore_appetite": 0, "help_with_insomnia": 0})

    side_effects = JSONField(default={"anxiety": 0, "dry_mouth": 0, "paranoia": 0,
                                      "headache": 0, "dizziness": 0, "dry_eyes": 0,
                                      "spacey": 0, "lazy": 0, "hungry": 0})

    flavor = JSONField(default={"ammonia": 0, "apple": 0, "apricot": 0, "berry": 0, "blue-cheese": 0,
                                "blueberry": 0, "buttery": 0, "cheese": 0, "chemical": 0, "chestnut": 0,
                                "citrus": 0, "coffee": 0, "diesel": 0, "earthy": 0, "flowery": 0,
                                "grape": 0, "grapefruit": 0, "herbal": 0, "honey": 0, "lavender": 0,
                                "lemon": 0, "lime": 0, "mango": 0, "menthol": 0, "minty": 0,
                                "nutty": 0, "orange": 0, "peach": 0, "pear": 0, "pepper": 0,
                                "pine": 0, "pineapple": 0, "plum": 0, "pungent": 0, "rose": 0,
                                "sage": 0, "skunk": 0, "spicy-herbal": 0, "strawberry": 0, "sweet": 0,
                                "tar": 0, "tea": 0, "tobacco": 0, "tree-fruit": 0, "tropical": 0,
                                "vanilla": 0, "violet": 0, "woody": 0})

    about = models.TextField(_('Description'), null=True, blank=True)
    origins = models.ManyToManyField('self', symmetrical=False, blank=True)

    removed_by = models.CharField(max_length=20, blank=True, null=True)
    removed_date = models.DateTimeField(blank=True, null=True)

    # social fields
    meta_desc = models.CharField(max_length=3072, blank=True)
    meta_keywords = models.CharField(max_length=3072, blank=True)

    @property
    def variety_image(self):
        return static('images/variety-{variety}.png'.format(variety=self.variety))

    @property
    def url(self):
        return self.get_absolute_url()

    def validate_image(field_file_obj):
        file_size = field_file_obj.file.size
        megabyte_limit = settings.MAX_IMAGE_SIZE
        if file_size > megabyte_limit:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    social_image = ResizedImageField(max_length=255, blank=True, help_text='Maximum file size allowed is 10Mb', validators=[validate_image], quality=75, size=[1024, 1024], upload_to=upload_to)


    def save(self, *args, **kwargs):
        if self.pk is None and not self.strain_slug:
            self.strain_slug = slugify(self.name)
        super(Strain, self).save(*args, **kwargs)

    def to_search_criteria(self):
        return {
            'strain_types': 'skipped',
            'effects': self.build_criteria_effects(self.effects),
            'benefits': self.build_criteria_effects(self.benefits),
            'side_effects': self.build_criteria_effects(self.side_effects)
        }

    def build_criteria_effects(self, effects_object):
        effects = []
        json = loads(dumps(effects_object))
        for key in json:
            value = json[key]
            if value > 0:
                effects.append({'name': key, 'value': value})
        return effects

    def get_absolute_url(self):
        return reverse('search:strain_detail', kwargs={'strain_variety': self.variety, 'slug_name': self.strain_slug})

    def __str__(self):
        return '{0} - {1}'.format(self.name, self.category)


def upload_image_to(instance, filename):
    return 'strains/{0}/images/{1}___{2}'.format(instance.strain.id, uuid4(), filename)


def validate_image(field_file_obj):
    file_size = field_file_obj.file.size
    megabyte_limit = settings.MAX_STRAIN_IMAGE_SIZE
    if file_size > megabyte_limit:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


@receiver(post_save, sender=Strain)
def create_es_strain(sender, **kwargs):
    strain = kwargs.get('instance')
    StrainESService().save_strain(strain)

    if User.objects.filter(email='tech+rate_bot@strainrx.co').exists():
        rate_bot = User.objects.get(email='tech+rate_bot@strainrx.co')
        if not StrainRating.objects.filter(strain=strain, created_by=rate_bot, removed_date=None).exists():
            r = StrainRating(strain=strain, created_by=rate_bot, effects=strain.effects, benefits=strain.benefits,
                             side_effects=strain.side_effects, status='pending')
            r.save()


@python_2_unicode_compatible
class StrainImage(models.Model):
    strain = models.ForeignKey(Strain, on_delete=models.DO_NOTHING, related_name='images')
    image = models.ImageField(max_length=255, upload_to=upload_image_to, blank=True,
                              help_text='Maximum file size allowed is 10Mb',
                              validators=[validate_image])

    created_date = models.DateField(blank=False, null=False, default=datetime.now)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    is_approved = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        i = self.image
        return i.url if i and i.url else None


@python_2_unicode_compatible
class Effect(models.Model):
    class Meta:
        unique_together = (("effect_type", "data_name"),)

    EFFECT_TYPE_CHOICES = (
        ('effect', 'Effect'),
        ('benefit', 'Benefit'),
        ('side_effect', 'Side Effect'),
    )

    effect_type = models.CharField(max_length=20, choices=EFFECT_TYPE_CHOICES)
    data_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return '{0} - {1}'.format(self.effect_type, self.display_name)


def upload_flavor_image_to(instance, filename):
    return 'flavors/images/{0}___{1}'.format(instance.data_name, filename)


def validate_flavor_image(field_file_obj):
    file_size = field_file_obj.file.size
    one_megabyte = 1 * 1024 * 1024
    if file_size > one_megabyte:
        raise ValidationError("Max file size is %sMB" % str(1))


@python_2_unicode_compatible
class Flavor(models.Model):
    data_name = models.SlugField(max_length=100, help_text='This will be slugified automatically from Display Name')
    display_name = models.CharField(max_length=100)
    image = models.ImageField(max_length=255, upload_to=upload_flavor_image_to, blank=True,
                              help_text='Maximum file size allowed is 1Mb',
                              validators=[validate_flavor_image])

    def save(self, *args, **kwargs):
        if self.pk is None and not self.data_name:
            self.data_name = slugify(self.display_name)
        super(Flavor, self).save(*args, **kwargs)

    def __str__(self):
        return '{0} ({1})'.format(self.data_name, self.display_name)


@python_2_unicode_compatible
class UserSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    varieties = JSONField(max_length=250)
    effects = JSONField(max_length=1000)
    benefits = JSONField(max_length=1000)
    side_effects = JSONField(max_length=1000)

    last_modified_date = models.DateTimeField(auto_now=True)

    def to_search_criteria(self):
        return {
            'strain_types': self.varieties,
            'effects': self.effects,
            'benefits': self.benefits,
            'side_effects': self.side_effects
        }

    def __str__(self):
        return '{0} - {1}'.format(self.user, self.last_modified_date)


@python_2_unicode_compatible
class StrainReview(models.Model):
    """
        A 5-star rating
    """
    strain = models.ForeignKey(Strain, on_delete=models.DO_NOTHING)

    rating = models.FloatField()
    review = models.TextField(default='', blank=True)
    review_approved = models.BooleanField(default=False)

    created_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='+')
    last_modified_date = models.DateTimeField()
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='+')

    def __init__(self, *args, **kwargs):
        #
        super().__init__(*args, **kwargs)
        self.__created_date = self.created_date
        self.__last_modified_date = self.last_modified_date

    def save(self, *args, **kwargs):
        # We want to have auto_now_add and auto_add behaviour but
        # also allow to edit the dates through admin

        if self.created_date is None:
            self.created_date = now()

        if self.last_modified_date == self.__last_modified_date:
            self.last_modified_date = now()

        super().save(*args, **kwargs)


@python_2_unicode_compatible
class StrainRating(models.Model):
    """
        A user's strain review, that user left via Disagree link in SPD
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
    )

    strain = models.ForeignKey(Strain, on_delete=models.DO_NOTHING)

    effects = JSONField(default={})
    effects_changed = models.BooleanField(default=False)

    benefits = JSONField(default={})
    benefits_changed = models.BooleanField(default=False)

    side_effects = JSONField(default={})
    side_effects_changed = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    removed_date = models.DateTimeField(null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='+')
    created_by_ip = models.CharField(max_length=30, blank=True, null=True)
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='+')
    last_modified_by_ip = models.CharField(max_length=30, blank=True, null=True)


@receiver(post_save, sender=StrainReview)
def create_es_review(sender, **kwargs):
    strain_review = kwargs.get('instance')
    es_serializer = StrainReviewESSerializer(strain_review)
    data = es_serializer.data
    data['created_by'] = strain_review.created_by.id
    data['last_modified_by'] = strain_review.last_modified_by.id if strain_review.last_modified_by else None
    StrainESService().save_strain_review(data, strain_review.id, strain_review.strain.id)


@python_2_unicode_compatible
class UserFavoriteStrain(models.Model):
    strain = models.ForeignKey(Strain, on_delete=models.DO_NOTHING)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now=True)

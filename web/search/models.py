from __future__ import unicode_literals, absolute_import

import os
from datetime import datetime
from uuid import uuid4

from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible

from web.users.models import User


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
                                      "headache": 0, "dizziness": 0, "dry_eyes": 0})

    flavor = JSONField(default={"ammonia": 0, "apple": 0, "apricot": 0, "berry": 0, "blue_cheese": 0,
                                "blueberry": 0, "buttery": 0, "cheese": 0, "chemical": 0, "chestnut": 0,
                                "citrus": 0, "coffee": 0, "diesel": 0, "earthy": 0, "flowery": 0,
                                "grape": 0, "grapefruit": 0, "herbal": 0, "honey": 0, "lavender": 0,
                                "lemon": 0, "lime": 0, "mango": 0, "menthol": 0, "minty": 0,
                                "nutty": 0, "orange": 0, "peach": 0, "pear": 0, "pepper": 0,
                                "pine": 0, "pineapple": 0, "plum": 0, "pungent": 0, "rose": 0,
                                "sage": 0, "skunk": 0, "spicy_herbal": 0, "strawberry": 0, "sweet": 0,
                                "tar": 0, "tea": 0, "tobacco": 0, "tree_fruit": 0, "tropical": 0,
                                "vanilla": 0, "violet": 0, "woody": 0})

    about = models.CharField(max_length=1500, null=True, blank=True)
    origins = models.ManyToManyField('self', symmetrical=False, blank=True)

    def save(self, *args, **kwargs):
        if self.pk is None and not self.strain_slug:
            self.strain_slug = '{0}-{1}'.format(slugify(self.name), slugify(self.category))
        super(Strain, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


def upload_image_to(instance, filename):
    return 'strains/{0}/images/{1}___{2}'.format(instance.strain.pk, uuid4(), filename)


def validate_image(field_file_obj):
    file_size = field_file_obj.file.size
    megabyte_limit = os.environ('MAX_STRAIN_IMAGE_SIZE')
    if file_size > megabyte_limit:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


@python_2_unicode_compatible
class StrainImage(models.Model):
    strain = models.ForeignKey(Strain, on_delete=models.DO_NOTHING)
    image = models.ImageField(max_length=255, upload_to=upload_image_to, blank=True,
                              help_text='Maximum file size allowed is 10Mb',
                              validators=[validate_image])

    created_date = models.DateField(blank=False, null=False, default=datetime.now)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

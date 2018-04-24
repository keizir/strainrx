from __future__ import unicode_literals, absolute_import

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from rest_framework import status

from .managers import SystemPropertyQuerySet

SYSTEM_PROPERTY_NAME = (
    ('rating_recalculation_size', 'Rating Recalculation Size'),
    ('max_delivery_radius', 'Max Delivery/Proximity Radius'),
    ('auto_email_verification_for_business', 'Auto Email Verification for Business Users'),
)


@python_2_unicode_compatible
class SystemProperty(models.Model):
    name = models.CharField(max_length=50, choices=SYSTEM_PROPERTY_NAME, unique=True)
    value = models.CharField(max_length=100, blank=False, null=False)

    objects = SystemPropertyQuerySet.as_manager()


class PermanentlyRemoved(models.Model):
    STATUS_CHOICES = (
        (status.HTTP_301_MOVED_PERMANENTLY, status.HTTP_301_MOVED_PERMANENTLY),
        (status.HTTP_410_GONE, status.HTTP_410_GONE)
    )

    url = models.CharField(max_length=255)
    redirect_url = models.CharField(max_length=255, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)

    def clean(self):
        if self.status == status.HTTP_301_MOVED_PERMANENTLY and not self.redirect_url:
            raise ValidationError({'redirect_url': 'This field is required.'})

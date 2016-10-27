# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

USER_TYPE = [
    ('admin', 'Admin'),
    ('business', 'Business'),
    ('consumer', 'Consumer')
]

GENDER = [
    ('male', 'Male'),
    ('female', 'Female'),
]


@python_2_unicode_compatible
class User(AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, null=True, max_length=255)

    is_age_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=USER_TYPE, default='consumer')

    city = models.CharField(_('City'), blank=True, null=True, max_length=100)
    state = models.CharField(_('State'), blank=True, null=True, max_length=50)
    zipcode = models.CharField(_('Zip Code'), blank=True, null=True, max_length=10)

    birth_month = models.CharField(_('Birth Month'), blank=True, null=True, max_length=20)
    birth_day = models.IntegerField(_('Birth Day'), blank=True, null=True)
    birth_year = models.IntegerField(_('Birth Year'), blank=True, null=True)

    gender = models.CharField(_('Gender'), choices=GENDER, blank=True, null=True, max_length=10)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})


@python_2_unicode_compatible
class PwResetLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, primary_key=True)
    token = models.CharField(max_length=100)
    last_modified_date = models.DateTimeField(auto_now=True)


@python_2_unicode_compatible
class UserSetting(models.Model):
    class Meta:
        unique_together = (("user", "setting_name"),)

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    setting_name = models.CharField(max_length=100)
    setting_value = JSONField(max_length=4096, default={})
    last_modified_date = models.DateTimeField(auto_now=True)

# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-08-22 06:59
from __future__ import unicode_literals

from django.db import migrations, models
import django_resized.forms
import web.businesses.models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0043_business_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesslocation',
            name='meta_desc',
            field=models.CharField(blank=True, max_length=3072),
        ),
        migrations.AddField(
            model_name='businesslocation',
            name='meta_keywords',
            field=models.CharField(blank=True, max_length=3072),
        ),
        migrations.AddField(
            model_name='businesslocation',
            name='social_image',
            field=django_resized.forms.ResizedImageField(blank=True, help_text='Maximum file size allowed is 10Mb', max_length=255, upload_to=web.businesses.models.upload_to, validators=[web.businesses.models.BusinessLocation.validate_image]),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-08-18 05:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0042_update_location_name_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
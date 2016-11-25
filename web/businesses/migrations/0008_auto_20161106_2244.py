# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-06 22:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0007_businesslocation_location_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesslocation',
            name='removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='businesslocation',
            name='removed_by',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='businesslocation',
            name='removed_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-01-26 14:53
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0054_businesslocationmenuupdaterequest_secret_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businesslocation',
            name='grow_details',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={'indoor': False, 'organic': False, 'outdoor': False, 'pesticide_free': False}, null=True),
        ),
    ]

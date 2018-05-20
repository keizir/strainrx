# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-05-04 13:04
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone


def update_cannabinoids(apps, schema_editor):
    Strain = apps.get_model('search', 'Strain')
    default = {'CBC': 0, 'CBD': 0, 'CBG': 0, 'CBN': 0, 'THC': 0, 'THCA': 0, 'THCV': 0}

    for strain in Strain.objects.all():
        cannabinoids = strain.cannabinoids or default
        cannabinoids.update({'CBDA': 0})
        strain.cannabinoids = cannabinoids
        strain.save()


def remove_cannabinoids(apps, schema_editor):
    Strain = apps.get_model('search', 'Strain')
    default = {'CBC': 0, 'CBD': 0, 'CBG': 0, 'CBN': 0, 'THC': 0, 'THCA': 0, 'THCV': 0}

    for strain in Strain.objects.all():
        if strain.cannabinoids:
            strain.cannabinoids.pop('CBDA')
        else:
            strain.cannabinoids = default

        strain.save()


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0052_auto_20180425_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strain',
            name='cannabinoids',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={'CBC': 0, 'CBD': 0, 'CBDA': 0, 'CBG': 0, 'CBN': 0, 'THC': 0, 'THCA': 0, 'THCV': 0}),
        ),
        migrations.AlterField(
            model_name='strainreview',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='strainreview',
            name='last_modified_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.RunPython(update_cannabinoids, remove_cannabinoids)
    ]
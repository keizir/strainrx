# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-04-13 09:33
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


def update_terpenes(apps, schema_editor):
    Strain = apps.get_model('search', 'Strain')
    default = {'camphene': 0, 'carene': 0, 'caryophyllene': 0, 'geraniol': 0, 'humulene': 0, 'limonene': 0,
               'linalool': 0, 'myrcene': 0, 'ocimene': 0, 'phellandrene': 0, 'pinene': 0, 'pulegone': 0, 'sabinene': 0,
               'terpineol': 0, 'terpinolene': 0, 'valencene': 0}

    for strain in Strain.objects.all():
        terpenes = strain.terpenes or default
        terpenes.update({'valencene': 0})
        strain.terpenes = terpenes
        strain.save()


def remove_terpenes(apps, schema_editor):
    Strain = apps.get_model('search', 'Strain')
    default = {'camphene': 0, 'carene': 0, 'caryophyllene': 0, 'geraniol': 0, 'humulene': 0, 'limonene': 0,
               'linalool': 0, 'myrcene': 0, 'ocimene': 0, 'phellandrene': 0, 'pinene': 0, 'pulegone': 0, 'sabinene': 0,
               'terpineol': 0, 'terpinolene': 0, 'valencene': 0}

    for strain in Strain.objects.all():
        if strain.terpenes:
            strain.terpenes.pop('valencene')
        else:
            strain.terpenes = default

        strain.save()


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0048_auto_20180323_1003'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='strainimage',
            options={'ordering': ('created_date',)},
        ),
        migrations.AlterModelOptions(
            name='usersearch',
            options={'ordering': ('-last_modified_date',)},
        ),
        migrations.AddField(
            model_name='strain',
            name='quick_picks',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={'cbd': 0, 'euphoria': 0, 'focus': 0, 'good vibes': 0, 'pain relief': 0, 'passion': 0, 'relaxation': 0, 'sleep': 0}),
        ),
        migrations.AlterField(
            model_name='strain',
            name='terpenes',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={'camphene': 0, 'carene': 0, 'caryophyllene': 0, 'geraniol': 0, 'humulene': 0, 'limonene': 0, 'linalool': 0, 'myrcene': 0, 'ocimene': 0, 'phellandrene': 0, 'pinene': 0, 'pulegone': 0, 'sabinene': 0, 'terpineol': 0, 'terpinolene': 0, 'valencene': 0}),
        ),

        migrations.RunPython(update_terpenes, remove_terpenes)
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-11-17 19:02
from __future__ import unicode_literals

from django.db import migrations


def populate_flavors(apps, schema_editor):
    Strain = apps.get_model('search', 'Strain')
    new_flavors = ['cherry', 'banana', 'sour', 'chocolate']

    for strain in Strain.objects.all():
        flavors = strain.flavor.keys()
        for key in new_flavors:
            if key not in flavors:
                strain.flavor[key] = 0
        strain.save()


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0056_auto_20181104_1255'),
    ]

    operations = [
        migrations.RunPython(populate_flavors, migrations.RunPython.noop)
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-25 19:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0023_auto_20161122_2239'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserStrainReview',
            new_name='StrainRating',
        ),
    ]

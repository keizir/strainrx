# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-29 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemproperty',
            name='name',
            field=models.CharField(choices=[('rating_recalculation_size', 'Rating Recalculation Size')], max_length=50, unique=True),
        ),
    ]
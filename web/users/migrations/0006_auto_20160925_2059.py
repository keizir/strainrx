# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-25 20:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0005_auto_20160925_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Name of User'),
        ),
    ]

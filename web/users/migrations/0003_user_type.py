# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-24 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_auto_20160924_1132'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('admin', 'Admin'), ('business', 'Business'), ('consumer', 'Consumer')],
                                   default='consumer', max_length=10),
        ),
    ]

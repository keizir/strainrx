# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-08-18 01:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0005_article_is_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='is_page',
        ),
    ]
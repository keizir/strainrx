# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-08-22 06:16
from __future__ import unicode_literals

from django.db import migrations
import django_resized.forms
import web.search.models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0038_auto_20170822_0604'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='strain',
            name='image',
        ),
        migrations.AddField(
            model_name='strain',
            name='social_image',
            field=django_resized.forms.ResizedImageField(blank=True, help_text='Maximum file size allowed is 10Mb', max_length=255, upload_to=web.common.models.upload_to, validators=[web.common.models.validate_image]),
        ),
    ]

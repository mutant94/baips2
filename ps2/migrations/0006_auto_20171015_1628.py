# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-15 14:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ps2', '0005_auto_20171015_1627'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='editors',
            new_name='editor',
        ),
    ]

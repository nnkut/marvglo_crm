# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-08 16:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marvglo', '0007_employee_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_cashier',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='saleitem',
            name='stock',
            field=models.IntegerField(default=0),
        ),
    ]
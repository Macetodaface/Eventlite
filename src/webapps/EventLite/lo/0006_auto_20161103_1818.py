# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-03 22:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('EventLite', '0005_auto_20161103_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='eventsInterested',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='EventLite.Event'),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='ticketsPurchased',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='EventLite.Ticket'),
        ),
        migrations.AlterField(
            model_name='seller',
            name='eventsHosting',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='EventLite.Event'),
        ),
    ]
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('derp', '0004_test_testgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='commit',
            name='name',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('derp', '0005_commit_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='command',
            field=models.CharField(default=b'None', max_length=256),
        ),
    ]

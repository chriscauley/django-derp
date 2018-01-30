# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('derp', '0003_testgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='testgroup',
            field=models.ForeignKey(blank=True, to='derp.TestGroup', null=True),
        ),
    ]

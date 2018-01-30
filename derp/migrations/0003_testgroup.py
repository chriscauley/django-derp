# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('derp', '0002_remove_test_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-order',),
            },
        ),
    ]

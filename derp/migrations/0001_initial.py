# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import derp.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=16, choices=[(b'url', b'url')])),
                ('name', models.CharField(help_text=b'Verbose Test being called (eg. a url, task, or function', max_length=128)),
                ('parameters', derp.fields.JSONField(default=dict)),
                ('parameters_hash', models.CharField(default=b'arst', max_length=32)),
                ('result', models.TextField(default=b'')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('commit_hash', models.CharField(max_length=32)),
                ('queries', models.IntegerField()),
                ('milliseconds', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('test', models.ForeignKey(to='derp.Test')),
            ],
        ),
    ]

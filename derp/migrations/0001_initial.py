# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import derp.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('order', models.IntegerField(default=0)),
                ('id', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='derp.Commit', null=True)),
            ],
            options={
                'ordering': ('-order',),
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=16, choices=[(b'url', b'URL'), (b'task', b'TASK')])),
                ('name', models.CharField(help_text=b'Verbose Test being called (eg. a url, task, or function', max_length=128)),
                ('parameters', derp.fields.JSONField(default=dict)),
                ('parameters_hash', models.CharField(default=b'arst', max_length=32)),
                ('result', models.TextField(default=b'')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('queries', models.IntegerField()),
                ('milliseconds', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'unknown', max_length=16, choices=[(b'pass', b'pass'), (b'fail', b'fail'), (b'unknown', b'unknown')])),
                ('commit', models.ForeignKey(blank=True, to='derp.Commit', null=True)),
                ('test', models.ForeignKey(to='derp.Test')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TestStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'unknown', max_length=16, choices=[(b'pass', b'pass'), (b'fail', b'fail'), (b'unknown', b'unknown')])),
                ('average_ms', models.IntegerField(default=0)),
                ('run_count', models.IntegerField(default=0)),
                ('commit', models.ForeignKey(to='derp.Commit')),
                ('test', models.ForeignKey(to='derp.Test')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

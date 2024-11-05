# Generated by Django 5.1.1 on 2024-11-04 08:49

import base.models
import django.contrib.auth.models
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_notificationtype_options_and_more'),
        ('systems', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIUser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('last_activity', models.DateTimeField(editable=False)),
                ('state', models.ForeignKey(default=base.models.State.active, on_delete=django.db.models.deletion.CASCADE, to='base.state')),
                ('system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='systems.system')),
            ],
            options={
                'ordering': ('-date_created',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]

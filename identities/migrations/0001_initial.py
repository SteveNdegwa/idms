# Generated by Django 5.1.1 on 2024-10-07 08:32

import base.models
import django.db.models.deletion
import utils.token_manager
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Identity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('token', models.CharField(default=utils.token_manager.generate_token, max_length=200)),
                ('expires_at', models.DateTimeField(default=utils.token_manager.token_expiry)),
                ('source_ip', models.GenericIPAddressField(blank=True, help_text='The originating IP Address.', null=True)),
                ('totp_key', models.CharField(blank=True, max_length=100, null=True)),
                ('totp_time_value', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.ForeignKey(default=base.models.State.active, on_delete=django.db.models.deletion.CASCADE, to='base.state')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
    ]
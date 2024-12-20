# Generated by Django 4.2.11 on 2024-10-09 13:11

import base.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_notificationtype_options_and_more'),
        ('identities', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identity',
            name='state',
            field=models.ForeignKey(default=base.models.State.activation_pending, on_delete=django.db.models.deletion.CASCADE, to='base.state'),
        ),
    ]

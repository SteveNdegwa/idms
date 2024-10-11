# Generated by Django 4.2.11 on 2024-10-09 13:11

import base.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_notificationtype_options_and_more'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='state',
            field=models.ForeignKey(default=base.models.State.active, on_delete=django.db.models.deletion.CASCADE, to='base.state'),
        ),
        migrations.AlterField(
            model_name='role',
            name='state',
            field=models.ForeignKey(default=base.models.State.active, on_delete=django.db.models.deletion.CASCADE, to='base.state'),
        ),
        migrations.AlterField(
            model_name='rolepermission',
            name='state',
            field=models.ForeignKey(default=base.models.State.active, on_delete=django.db.models.deletion.CASCADE, to='base.state'),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.ForeignKey(blank=True, default=base.models.State.active, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.state'),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('id_no', models.CharField(blank=True, max_length=100, null=True)),
                ('other_phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('occupation', models.CharField(blank=True, max_length=100, null=True)),
                ('employment_type', models.CharField(choices=[('Self Employed', 'Self Employed'), ('Employed', 'Employed'), ('Unemployed', 'Unemployed'), ('Freelance', 'Freelance'), ('Student', 'Student')], default='Other', max_length=100)),
                ('income_from_investments', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('currency', models.CharField(blank=True, max_length=100, null=True)),
                ('net_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('work_place_grants_or_allowance', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('physical_work_address', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.ForeignKey(default=base.models.Country.default_country, on_delete=django.db.models.deletion.CASCADE, related_name='profile_country', to='base.country')),
                ('country_of_work', models.ForeignKey(default=base.models.Country.default_country, on_delete=django.db.models.deletion.CASCADE, to='base.country')),
                ('state', models.ForeignKey(blank=True, default=base.models.State.active, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.state')),
            ],
            options={
                'verbose_name': 'CustomerProfileInformation',
                'verbose_name_plural': 'CustomerProfileInformation',
                'ordering': ('-date_created',),
            },
        ),
        migrations.AddField(
            model_name='user',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.profile'),
        ),
    ]

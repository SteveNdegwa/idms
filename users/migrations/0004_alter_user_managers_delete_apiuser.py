# Generated by Django 5.1.1 on 2024-11-05 04:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_apiuser_last_activity'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
            ],
        ),
        migrations.DeleteModel(
            name='APIUser',
        ),
    ]

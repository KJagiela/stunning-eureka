# Generated by Django 3.2.11 on 2022-10-31 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grabbo', '0006_add_seniority'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='is_blacklisted',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 3.2.11 on 2023-01-07 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grabbo', '0008_job_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='is_blacklisted',
            field=models.BooleanField(default=False),
        ),
    ]

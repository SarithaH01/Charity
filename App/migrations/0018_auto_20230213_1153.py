# Generated by Django 3.2.7 on 2023-02-13 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0017_donation_to_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='from_user',
            field=models.CharField(blank=True, max_length=5000),
        ),
        migrations.AddField(
            model_name='track',
            name='to_user',
            field=models.CharField(blank=True, max_length=5000),
        ),
    ]

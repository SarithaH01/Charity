# Generated by Django 3.2.7 on 2023-02-13 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0015_track'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='charityName',
            field=models.CharField(default='', max_length=50000),
            preserve_default=False,
        ),
    ]
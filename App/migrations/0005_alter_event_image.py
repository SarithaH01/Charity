# Generated by Django 3.2.7 on 2023-02-03 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0004_auto_20230203_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(default='sherlock.jpg', upload_to='events'),
        ),
    ]

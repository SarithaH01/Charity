# Generated by Django 3.2.7 on 2023-02-27 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0025_product_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='added_by_organization',
            field=models.BooleanField(default=False),
        ),
    ]

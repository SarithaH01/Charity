# Generated by Django 3.2.7 on 2023-03-26 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0026_product_added_by_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='account_type',
            field=models.CharField(blank=True, max_length=5000),
        ),
    ]
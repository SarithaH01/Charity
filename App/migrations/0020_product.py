# Generated by Django 3.2.7 on 2023-02-27 14:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('App', '0019_donation_sent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=5000)),
                ('description', models.CharField(max_length=5000)),
                ('category', models.CharField(max_length=50000)),
                ('image', models.ImageField(default='sherlock.jpg', upload_to='blog')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('price', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
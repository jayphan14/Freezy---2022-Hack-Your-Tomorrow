# Generated by Django 3.2.7 on 2022-02-05 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_remove_listing_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='location',
            field=models.CharField(default='', max_length=255),
        ),
    ]

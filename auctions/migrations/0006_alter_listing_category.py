# Generated by Django 3.2.7 on 2022-02-05 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20201012_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('a', 'Asian'), ('b', 'European'), ('c', 'Gluten Free'), ('d', 'Low Fat'), ('e', 'Keto'), ('f', 'None')], default='None', max_length=1),
        ),
    ]

# Generated by Django 3.2.7 on 2021-09-25 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_auctionlistings_imageurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlistings',
            name='imageUrl',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]

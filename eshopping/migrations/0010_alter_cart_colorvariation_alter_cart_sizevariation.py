# Generated by Django 4.2 on 2025-03-05 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eshopping', '0009_rename_price_order_totalamount_remove_order_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='colorVariation',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='sizeVariation',
            field=models.CharField(max_length=50, null=True),
        ),
    ]

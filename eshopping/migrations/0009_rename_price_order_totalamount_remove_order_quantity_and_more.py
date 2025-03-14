# Generated by Django 4.2 on 2025-03-05 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eshopping', '0008_remove_order_product_remove_order_product_size_color_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='price',
            new_name='totalAmount',
        ),
        migrations.RemoveField(
            model_name='order',
            name='quantity',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]

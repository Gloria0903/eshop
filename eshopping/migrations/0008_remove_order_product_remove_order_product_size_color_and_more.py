# Generated by Django 4.2 on 2025-03-05 13:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eshopping', '0007_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='product',
        ),
        migrations.RemoveField(
            model_name='order',
            name='product_size_color',
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='eshopping.color')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eshopping.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eshopping.product')),
                ('size', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='eshopping.size')),
            ],
        ),
    ]

# Generated by Django 4.2.7 on 2023-11-25 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=180)),
                ('selling_price', models.FloatField()),
                ('discounted_price', models.FloatField()),
                ('description', models.TextField()),
                ('composition', models.TextField(default='')),
                ('prodeshopping', models.TextField(default='')),
                ('category', models.CharField(choices=[('MN', 'Mens_clothing'), ('WN', 'Womens_clothing'), ('BC', 'Babys_clothing'), ('SH', 'Shirts'), ('JE', 'Jeans'), ('SW', 'Swimwear'), ('SL', 'Sleepingwear'), ('SP', 'Sportswear'), ('JP', 'Jumpsuits'), ('BL', 'Blazers'), ('JK', 'Jackets'), ('SH', 'Shoes')], max_length=2)),
                ('product_image', models.ImageField(upload_to='product')),
            ],
        ),
    ]

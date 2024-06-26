# Generated by Django 4.1 on 2024-03-24 07:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choapp', '0008_remove_posts_image_url_posts_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='results',
            name='image_url',
        ),
        migrations.AddField(
            model_name='results',
            name='image',
            field=models.ImageField(default='', upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='product_categories',
            name='category_name',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='reactions',
            name='boost_score',
            field=models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterModelTable(
            name='products',
            table='products',
        ),
    ]

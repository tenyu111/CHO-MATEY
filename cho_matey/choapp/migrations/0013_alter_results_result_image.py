# Generated by Django 4.1 on 2024-03-28 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choapp', '0012_remove_results_content_remove_results_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='results',
            name='result_image',
            field=models.ImageField(blank=True, upload_to='result_images/'),
        ),
    ]

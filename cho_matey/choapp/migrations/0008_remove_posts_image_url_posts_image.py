# Generated by Django 4.1 on 2024-03-24 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choapp', '0007_rename_is_staff_users_is_admin_remove_users_groups_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posts',
            name='image_url',
        ),
        migrations.AddField(
            model_name='posts',
            name='image',
            field=models.ImageField(default='', upload_to='images/'),
        ),
    ]
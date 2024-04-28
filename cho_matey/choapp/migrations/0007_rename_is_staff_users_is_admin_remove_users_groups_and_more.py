# Generated by Django 4.1 on 2024-03-23 23:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('choapp', '0006_remove_users_email_alter_users_username'),
    ]

    operations = [
        migrations.RenameField(
            model_name='users',
            old_name='is_staff',
            new_name='is_admin',
        ),
        migrations.RemoveField(
            model_name='users',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='users',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='users',
            name='is_superuser',
        ),
        migrations.RemoveField(
            model_name='users',
            name='user_permissions',
        ),
    ]

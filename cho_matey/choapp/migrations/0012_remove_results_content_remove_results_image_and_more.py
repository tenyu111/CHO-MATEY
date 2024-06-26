# Generated by Django 4.1 on 2024-03-28 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choapp', '0011_alter_posts_price_alter_reactions_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='results',
            name='content',
        ),
        migrations.RemoveField(
            model_name='results',
            name='image',
        ),
        migrations.AddField(
            model_name='results',
            name='result_comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='results',
            name='result_image',
            field=models.ImageField(blank=True, default='', upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='results',
            name='result_category',
            field=models.IntegerField(choices=[(0, '買った'), (1, '別の商品を買った'), (2, '踏みとどまった')]),
        ),
    ]

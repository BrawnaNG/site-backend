# Generated by Django 3.2.18 on 2024-09-19 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0003_auto_20240919_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='title',
            field=models.TextField(default='Title'),
            preserve_default=False,
        ),
    ]

# Generated by Django 3.2.18 on 2024-09-20 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0004_story_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='story',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
# Generated by Django 5.1.4 on 2024-12-27 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0009_alter_story_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='title',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='story',
            name='brief',
            field=models.TextField(blank=True, default=''),
        ),
    ]
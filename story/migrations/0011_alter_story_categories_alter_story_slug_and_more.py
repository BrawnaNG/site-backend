# Generated by Django 5.1.4 on 2025-01-14 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0006_alter_category_description'),
        ('story', '0010_alter_chapter_title_alter_story_brief'),
        ('tag', '0004_tag_old_brawna_term_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='categories',
            field=models.ManyToManyField(to='category.category'),
        ),
        migrations.AlterField(
            model_name='story',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='story',
            name='tags',
            field=models.ManyToManyField(to='tag.tag'),
        ),
    ]

# Generated by Django 3.2.18 on 2024-10-06 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0003_alter_tag_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='old_brawna_term_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
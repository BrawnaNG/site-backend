# Generated by Django 3.2.18 on 2024-10-04 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_saved_stories'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='old_brawna_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
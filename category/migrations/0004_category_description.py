# Generated by Django 3.2.18 on 2024-09-25 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0003_alter_category_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.CharField(max_length=200, null=True),
        ),
    ]

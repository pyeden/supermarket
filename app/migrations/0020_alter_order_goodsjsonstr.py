# Generated by Django 3.2.5 on 2022-01-24 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20220124_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='goodsJsonStr',
            field=models.JSONField(blank=True, default=[], null=True),
        ),
    ]

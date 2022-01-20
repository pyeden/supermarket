# Generated by Django 3.2.5 on 2022-01-18 14:56

import app.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20220118_2238'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goods',
            old_name='dateEndInt',
            new_name='dateEnd',
        ),
        migrations.RemoveField(
            model_name='goods',
            name='dateStartInt',
        ),
        migrations.AddField(
            model_name='goods',
            name='dateEndCountDown',
            field=app.models.TimeStampField(blank=True, default=0, null=True, verbose_name='倒计时'),
        ),
        migrations.AddField(
            model_name='goods',
            name='dateEndPingtuan',
            field=app.models.TimeStampField(blank=True, default=0, null=True, verbose_name='拼团时间'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='categoryId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.goodscategory'),
        ),
    ]
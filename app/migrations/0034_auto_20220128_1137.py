# Generated by Django 3.2.5 on 2022-01-28 03:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_alter_order_numbers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='prices',
            new_name='amountReal',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='numbers',
            new_name='goodsNumber',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='pay_prices',
            new_name='payPrices',
        ),
    ]

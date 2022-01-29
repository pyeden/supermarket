# Generated by Django 3.2.5 on 2022-01-28 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_auto_20220128_1137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='cityId',
        ),
        migrations.RemoveField(
            model_name='order',
            name='deductionScore',
        ),
        migrations.RemoveField(
            model_name='order',
            name='districtId',
        ),
        migrations.RemoveField(
            model_name='order',
            name='extJsonStr',
        ),
        migrations.RemoveField(
            model_name='order',
            name='provinceId',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shopName',
        ),
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(blank=True, default='0', max_length=255, null=True, verbose_name='买家地址'),
        ),
        migrations.AlterField(
            model_name='order',
            name='goodsType',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='linkMan',
            field=models.CharField(blank=True, default='0', max_length=255, null=True, verbose_name='买家昵称'),
        ),
        migrations.AlterField(
            model_name='order',
            name='orderNumber',
            field=models.CharField(blank=True, default='0', max_length=255, null=True, verbose_name='订单编号'),
        ),
        migrations.AlterField(
            model_name='order',
            name='peisongType',
            field=models.CharField(blank=True, choices=[('kd', '需要配送'), ('zq', '上门自取')], default='zq', max_length=255, null=True, verbose_name='取货方式'),
        ),
        migrations.AlterField(
            model_name='order',
            name='shopId',
            field=models.IntegerField(blank=True, choices=[(1, '嘉鑫超市'), (2, '百货超市')], default=1, null=True, verbose_name='取货超市'),
        ),
    ]

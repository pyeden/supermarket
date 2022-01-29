import json
from collections import OrderedDict

# Register your models here.
from decimal import Decimal

from django.utils.html import format_html

from .models import *

from django.contrib import admin
from django.apps import apps
from django.utils.text import capfirst


def find_app_index(app_label):
    app = apps.get_app_config(app_label)
    main_menu_index = getattr(app, 'main_menu_index', 9999)
    return main_menu_index


def find_model_index(name):
    count = 0
    for model, model_admin in admin.site._registry.items():
        if capfirst(model._meta.verbose_name_plural) == name:
            return count
        else:
            count += 1
    return count


def index_decorator(func):
    def inner(*args, **kwargs):
        templateresponse = func(*args, **kwargs)
        app_list = templateresponse.context_data['app_list']
        app_list.sort(key=lambda r: find_app_index(r['app_label']))
        for app in app_list:
            app['models'].sort(key=lambda x: find_model_index(x['name']))
        return templateresponse

    return inner


registry = OrderedDict()
registry.update(admin.site._registry)
admin.site._registry = registry
admin.site.index = index_decorator(admin.site.index)
admin.site.app_index = index_decorator(admin.site.app_index)


class BaseAdmin(admin.ModelAdmin):
    # 每页显示的数量
    # list_per_page = 15
    # 分页控件，使用django默认控件
    # paginator = Paginator
    # 列表顶部，设置为False不在顶部显示，默认为True。
    actions_on_top = True
    # 列表底部，设置为False不在底部显示，默认为False。
    actions_on_bottom = False


@admin.register(Goods)
class GoodsAdmin(BaseAdmin):
    # 列表中显示的字段（表头）
    list_display = [
        'name',
        'characteristic',
        'minPrice',
        'originalPrice',
        'recommendStatus',
        'status',
        'number',
        'dateProduction',
        'day_due',
        'short_pic'
    ]
    # 设置排序字段，负号表示降序排序
    ordering = ('id',)
    # 设置点击哪些字段可以点击进入编辑界面，默认为id字段
    list_display_links = [
        'name',
        'characteristic',
        'minPrice',
        'originalPrice',
        'recommendStatus',
        'status',
        'number',
        'dateProduction',
        'day_due',
        'short_pic'
    ]
    # 搜索框，是一个列表，列表中是作为搜索依据的字段
    search_fields = []
    # 设置详细页面中的只读字段，此时不能在详细页面进行更改。
    readonly_fields = ()
    # 在详细页面中以单选按钮显示
    # radio_fields = {"goods_order_status": admin.HORIZONTAL} # 或者admin.VERTICAL
    # 设置详情页面的字段顺序以及显示的字段
    # fields = ('goods_order_id', 'price', 'count')
    # 设置在详情页同一行显示的字段
    # 'goods_order_id', 'price'将在同一行显示
    # fields = (('goods_order_id', 'price'), 'count')

    def day_due(self, obj):
        # 生产日期和保质期减去当前时间=过期剩余时间
        res = obj.dateProduction - datetime.datetime.now() + datetime.timedelta(days=obj.dayDue * 30)
        seconds = res.total_seconds()
        if seconds <= 0:
            return '已过期'
        hours = Decimal((seconds // 3600)).quantize(Decimal('0'))
        minutes = Decimal(((seconds % 3600) // 60)).quantize(Decimal('0'))
        seconds = Decimal((seconds % 60)).quantize(Decimal('0.00'))
        return f'{hours}小时 {minutes}分钟 {seconds} 秒'
    day_due.short_description = format_html('<a style="Color:#049EFF;" >{}</a>', '过期时间')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # return qs.filter(isdebug=0)
        return qs


@admin.register(GoodsCategory)
class GoodsCategoryAdmin(BaseAdmin):
    # 列表中显示的字段（表头）
    list_display = [
        'name',
        'key',
        'type',
        'icon',
    ]
    # 设置排序字段，负号表示降序排序
    ordering = ('id',)
    # 设置点击哪些字段可以点击进入编辑界面，默认为id字段
    list_display_links = [
        'name',
        'key',
        'type',
        'icon',
    ]
    # 搜索框，是一个列表，列表中是作为搜索依据的字段
    search_fields = []
    # 设置详细页面中的只读字段，此时不能在详细页面进行更改。
    readonly_fields = ()
    # 在详细页面中以单选按钮显示
    # radio_fields = {"goods_order_status": admin.HORIZONTAL} # 或者admin.VERTICAL
    # 设置详情页面的字段顺序以及显示的字段
    # fields = ('goods_order_id', 'price', 'count')
    # 设置在详情页同一行显示的字段
    # 'goods_order_id', 'price'将在同一行显示
    # fields = (('goods_order_id', 'price'), 'count')


@admin.register(Config)
class ConfigAdmin(BaseAdmin):
    # 列表中显示的字段（表头）
    list_display = [
        'key',
        'value',
        'remark',
    ]
    ordering = ('id',)
    list_display_links = [
        'key',
        'value',
        'remark',
    ]
    search_fields = []
    readonly_fields = ()


@admin.register(Order)
class OrderAdmin(BaseAdmin):
    # 列表中显示的字段（表头）
    list_display = [
        'orderNumber',
        'payPrices',
        'goodsNumber',
        'order_goods_detail',
        'linkMan',
        'mobile',
        'address',
        'peisongType',
        'remark',
        'userId',
    ]
    ordering = ('id',)
    list_display_links = [
        'orderNumber',
        'payPrices',
        'goodsNumber',
        'order_goods_detail',
        'linkMan',
        'mobile',
        'address',
        'peisongType',
        'remark',
        'userId',
    ]
    search_fields = []
    readonly_fields = ()

    def order_goods_detail(self, obj):
        goods_list = json.loads(obj.goodsJsonStr)

        detail_str = ''
        for goods in goods_list:
            detail_str += f"{goods['name']} - {goods['number']} \n"
        return detail_str

    order_goods_detail.short_description = format_html('<a style="Color:#049EFF;" >{}</a>', '订单商品详情')


@admin.register(ShopAddress)
class ShopAddressAdmin(BaseAdmin):
    # 列表中显示的字段（表头）
    list_display = [
        'address',
        'name',
        'linkPhone',
    ]
    ordering = ('id',)
    list_display_links = [
        'address',
        'name',
        'linkPhone',
    ]
    search_fields = []
    readonly_fields = ()


admin.site.site_header = '嘉鑫超市管理系统'
admin.site.site_title = '嘉鑫超市管理系统'
admin.site.index_title = '嘉鑫超市管理系统'

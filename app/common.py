from django.db import connections

from utils import common_utils, exception_utils
from app import models as mo
from app import serializers as se


class Car:

    def __init__(self, openid=None):
        self.data = []
        self.openid = openid

    def parse_data(self):
        number = 0
        price = 0
        score = 0
        goods_status = []
        for goods in self.data:
            status = {}
            goods_number = goods.get('number', 0)
            number += goods_number
            price += float(goods.get('price', 0)) * float(goods_number)
            score += float(goods.get('score', 0)) * float(goods_number)

            status["id"] = goods["id"]
            status["sellEnd"] = goods["sellEnd"]
            status["sellStart"] = goods["sellStart"]
            status["status"] = goods["status"]
            status["statusStr"] = goods["statusStr"]
            status["stores"] = goods.get('gotScore', 0)
            goods_status.append(status)

        json_data = {
            "number": number,  # 购物车商品总数量
            "score": score,   # 需要消耗的积分
            "shopList": [    # 门店列表 默认0
                {
                    "id": 0,
                    "name": "",
                    "serviceDistance": 99999999
                }
            ],
            "goodsStatus": goods_status,
            "price": price,  # 结算总价
            "items": self.data
        }
        return json_data

    def get_car_data(self):
        try:
            with connections['default'].cursor() as cursor:
                select = ','.join([
                    "category_id as categoryId", "key", "shopId", "pic", "name",
                    "name as subName", "minBuyNumber", "weight", "logisticsId", "minPrice as price", "selected", "stores",
                    "status", "statusStr", "sellEnd", "sellStart", "status", "statusStr", "stores",
                ])
                sql = f'select {select}, c.id as id,g.minScore as score, g.id as goodsId, c.number as number from app_shopcart as c '\
                      'left join app_goods as g on c.goodsId = g.id where c.user_id = %s and c.is_delete=0'
                cursor.execute(sql, [self.openid])
                self.data = common_utils.dict_fetchall(cursor)
        except Exception as e:
            raise exception_utils.DbFailed(detail=e)


class Goods:

    def __init__(self, goods_id):
        self.id = goods_id
        self.goods_query_set = self.get_goods_by_id()
        self.goods = self.goods_query_set.first()

    def get_goods_by_id(self):
        return mo.Goods.objects.filter(id=self.id)

    def basic_info(self):
        serializer = se.GoodsSerializer(self.goods)
        return serializer.data

    def parse_data(self):
        json_data = {
            'pics2': [],
            'skuList': [],
            'subPics': [],
            'logistics': {},
            'extJson': {},
            'category': {},
            'pics': [],
            'content': '',
            'properties': [],
            'basicInfo': self.basic_info()
        }

        return json_data
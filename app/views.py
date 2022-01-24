import json

from cryptography.fernet import Fernet
from django.contrib.auth.models import User, Group
from django.db import connections
from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from app import models as mo
from app import common
from app.paginations import NoticeListPagination
from app import serializers as se
from utils import wx_utils, exception_utils, common_utils


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = se.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = se.GroupSerializer
    permission_classes = []

    def get_queryset(self):
        params = self.request.query_params.dict()
        queryset = super().get_queryset().filter(**params).order_by('-list_order')
        return queryset


class ConfigList(APIView):
    """获取网站配置信息
    """

    def get(self, request):
        params = request.query_params.dict()
        query_set = mo.Config.objects.all()
        serializer = se.ConfigSerializer(query_set, many=True)
        json_data = {
            "code": 0,
            "data": serializer.data,
            "msg": "success"
        }
        return Response(json_data)


class WxAppLogin(APIView):
    """
    微信登陆
    """

    def post(self, request):
        json_data = {
            "code": 0,
            "msg": "success",
            'data': {}
        }
        return Response(json_data)


class WxAppAuthorize(APIView):
    """
    微信认证获取
    """

    def post(self, request):
        code = request.data.get('code', '093zjbGa17kttC0pC5Ha1D1vSR1zjbG3')
        res = wx_utils.get_wx_auth_session(code)
        session_key = res.get('session_key')
        openid = res.get('openid')
        if not session_key or not openid:
            raise exception_utils.WXFailed("微信服务器认证失败")

        obj = wx_utils.Wx3rdSession(openid=openid, session_key=session_key)
        obj.save_session_info()
        token = obj.token
        json_data = {
            "code": 0,
            "msg": "success",
            'data': {'token': token, 'uid': openid}
        }
        return Response(json_data)


class CheckToken(APIView):
    """
    微信认证获取
    """

    def get(self, request):
        token = request.data.get('token', '093zjbGa17kttC0pC5Ha1D1vSR1zjbG3')

        json_data = {
            "code": 0,
            "msg": "success",
            'data': {}
        }
        return Response(json_data)


class BannerList(APIView):
    """
    轮播图列表
    """

    def get(self, request):
        params = request.query_params.dict()
        query_set = mo.Banner.objects.filter(**params).all()
        serializer = se.BannersSerializer(query_set, many=True)
        json_data = {
            "code": 0,
            "data": serializer.data,
            "msg": "success"
        }
        return Response(json_data)


class CategoryAll(APIView):
    """
    商品分类列表.
    """

    def get(self, request):
        params = request.query_params.dict()
        query_set = mo.GoodsCategory.objects.filter(**params).all()
        serializer = se.GoodsCategorySerializer(query_set, many=True)
        json_data = {
            "code": 0,
            "data": serializer.data,
            "msg": "success"
        }
        return Response(json_data)


class ShopGoodsList(APIView):
    """商品列表，分页返回，每条20.
    """

    def post(self, request):
        params = request.data
        category_id = params.get('categoryId')
        recommend_status = params.get('recommendStatus')
        miao_sha = params.get('miaosha')
        query_set = mo.Goods.objects.all()
        if category_id:
            query_set = query_set.filter(category_id=category_id)
        if recommend_status:
            query_set = query_set.filter(recommendStatus=recommend_status)
        if miao_sha:
            query_set = query_set.filter(miaosha=miao_sha)

        pg = NoticeListPagination()
        page_data = pg.paginate_queryset(queryset=query_set, request=request, view=self)
        serializer = se.GoodsSerializer(page_data, many=True)
        json_data = {
            "code": 0,
            "data": serializer.data,
            "msg": "success"
        }
        return Response(json_data)


class ShopGoodsDetail(APIView):
    """商品列表，分页返回，每条20.
    """

    def get(self, request):
        params = request.query_params.dict()
        goods_id = params.get('id')
        open_id = wx_utils.get_openid(params.get('token'))
        g = common.Goods(goods_id=goods_id)
        data = g.parse_data()
        json_data = {
            "code": 0,
            "data": data,
            "msg": "success"
        }
        return Response(json_data)


class NoticeList(APIView):
    """
    首页公告
    """

    def post(self, request):
        params = request.data
        query_set = mo.Notice.objects.filter().all()
        pg = NoticeListPagination()
        page_data = pg.paginate_queryset(queryset=query_set, request=request, view=self)
        data = se.NoticeSerializer(page_data, many=True)
        json_data = {
            "code": 0,
            "data": {
                "totalRow": pg.page.paginator.count,
                "totalPage": pg.page.paginator.num_pages,
                "dataList": data.data
            },
            "msg": "success"
        }
        return Response(json_data)


class SiteAdPositionInfo(APIView):
    """
    活动海报图片
    """

    def get(self, request):
        params = request.query_params.dict()  # 'index-live-pic'
        query_set = mo.HomeAdvertising.objects.filter(**params).all()
        serializer = se.HomeAdvertisingSerializer(query_set, many=True)
        json_data = {
            "code": 0,
            "data": serializer.data,
            "msg": "success"
        }
        return Response(json_data)


class SiteGoodsDynamic(APIView):
    """
    商品购买动态.
    """

    def get(self, request):
        params = request.query_params.dict()
        query_set = mo.SiteGoodsDynamic.objects.filter().all()
        serializer = se.SiteGoodsDynamicSerializer(query_set, many=True)
        json_data = {
            "code": 0,
            "data": serializer.data,
            "msg": "success"
        }
        return Response(json_data)


class ShopCart(APIView):
    """获取购物车信息"""

    def get(self, request):
        params = request.query_params
        open_id = wx_utils.get_openid(params.get('token'))
        car = common.Car(openid=open_id)
        car.get_car_data()
        data = car.parse_data()
        json_data = {
            "code": 0,
            "data": data,
            "msg": "success"
        }
        return Response(json_data)


class ShopCartGoodsAdd(APIView):
    """获取购物车信息"""

    def post(self, request):
        params = request.data
        filter_data = {
            'goodsId': params.get('goodsId'),
            'number': params.get('number'),
            'user_id': wx_utils.get_openid(params.get('token')),
            'key': Fernet.generate_key().decode('utf-8'),
        }
        car_goods = mo.ShopCart.objects.filter(goodsId=params.get('goodsId')).first()
        if not car_goods:
            mo.ShopCart.objects.create(**filter_data)
        else:
            car_goods.number += int(params.get('number'))
            car_goods.save()

        json_data = {
            "code": 0,
            "data": {},
            "msg": "success"
        }
        return Response(json_data)


class ShopCartGoodsUpdate(APIView):
    """获取购物车信息"""

    def post(self, request):
        params = request.data
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')
        number = params.get('number')
        goods = mo.ShopCart.objects.filter(user_id=open_id, key=key).first()
        goods.number = number
        goods.save()
        json_data = {
            "code": 0,
            "data": {},
            "msg": "success"
        }
        return Response(json_data)


class ShopCartGoodsRemove(APIView):
    """获取购物车信息"""

    def post(self, request):
        params = request.data
        open_id = wx_utils.get_openid(params.get('token'))
        keys = params.get('key')
        key_list = keys.split(',') if keys else []
        goods = mo.ShopCart.objects.filter(user_id=open_id).filter(key__in=key_list).first()
        goods.delete()
        json_data = {
            "code": 0,
            "data": {},
            "msg": "success"
        }
        return Response(json_data)


class DefaultShopAddress(APIView):

    def get(self, request):
        params = request.query_params.dict()
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')

        json_data = {
            "code": 0,
            "data": {
                "extJson": {},
                "info": {
                    "address": "测试详细地址",
                    "areaStr": "峰峰矿区",
                    "cityId": "130400000000",
                    "cityStr": "邯郸市",
                    "dateAdd": "2021-10-24 21:52:32",
                    "dateUpdate": "2022-01-01 10:16:12",
                    "districtId": "130406000000",
                    "id": 265498,
                    "isDefault": False,
                    "linkMan": "测试",
                    "mobile": "13500000000",
                    "provinceId": "130000000000",
                    "provinceStr": "河北省",
                    "status": 0,
                    "statusStr": "正常",
                    "uid": 1351478,
                    "userId": 951
                }
            },
            "msg": "success"
        }
        return Response(json_data)


class ShopAddressList(APIView):

    def get(self, request):
        params = request.query_params.dict()
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')

        json_data = {
            "code": 0,
            "data": {
                "result": [
                    {
                        "address": "新港中路397号",
                        "areaStr": "海珠区",
                        "cityId": "440100000000",
                        "cityStr": "广州市",
                        "dateAdd": "2022-01-01 10:08:08",
                        "dateUpdate": "2022-01-01 10:11:25",
                        "districtId": "440105000000",
                        "id": 1,
                        "isDefault": True,
                        "linkMan": "张三",
                        "mobile": "020-81167888",
                        "provinceId": "440000000000",
                        "provinceStr": "广东省",
                        "status": 0,
                        "statusStr": "正常",
                        "uid": 1351478,
                        "userId": 951
                    }
                ],
                "totalRow": 3,
                "totalPage": 1
            },
            "msg": "success"
        }
        return Response(json_data)


class ShopAddressDetail(APIView):

    def get(self, request):
        params = request.query_params.dict()
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')

        json_data = {
            "code": 0,
            "data": {
                "extJson": {},
                "info": {
                    "address": "测试详细地址",
                    "areaStr": "峰峰矿区",
                    "cityId": "130400000000",
                    "cityStr": "邯郸市",
                    "dateAdd": "2021-10-24 21:52:32",
                    "dateUpdate": "2022-01-01 10:16:12",
                    "districtId": "130406000000",
                    "id": 1,
                    "isDefault": False,
                    "linkMan": "测试",
                    "mobile": "13500000000",
                    "provinceId": "130000000000",
                    "provinceStr": "河北省",
                    "status": 0,
                    "statusStr": "正常",
                    "uid": 1351478,
                    "userId": 951
                }
            },
            "msg": "success"
        }
        return Response(json_data)


class ShopAddressAdd(APIView):

    def post(self, request):
        params = request.data
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')

        json_data = {
            "code": 0,
            "data": {
                "extJson": {},
                "info": {
                    "address": "测试详细地址",
                    "areaStr": "峰峰矿区",
                    "cityId": "130400000000",
                    "cityStr": "邯郸市",
                    "dateAdd": "2021-10-24 21:52:32",
                    "dateUpdate": "2022-01-01 10:16:12",
                    "districtId": "130406000000",
                    "id": 1,
                    "isDefault": False,
                    "linkMan": "测试",
                    "mobile": "13500000000",
                    "provinceId": "130000000000",
                    "provinceStr": "河北省",
                    "status": 0,
                    "statusStr": "正常",
                    "uid": 1351478,
                    "userId": 951
                }
            },
            "msg": "success"
        }
        return Response(json_data)


class ShopAddressUpdate(APIView):

    def post(self, request):
        params = request.data
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')

        json_data = {
            "code": 0,
            "data": {
                "extJson": {},
                "info": {
                    "address": "测试详细地址",
                    "areaStr": "峰峰矿区",
                    "cityId": "130400000000",
                    "cityStr": "邯郸市",
                    "dateAdd": "2021-10-24 21:52:32",
                    "dateUpdate": "2022-01-01 10:16:12",
                    "districtId": "130406000000",
                    "id": 1,
                    "isDefault": False,
                    "linkMan": "测试",
                    "mobile": "13500000000",
                    "provinceId": "130000000000",
                    "provinceStr": "河北省",
                    "status": 0,
                    "statusStr": "正常",
                    "uid": 1351478,
                    "userId": 951
                }
            },
            "msg": "success"
        }
        return Response(json_data)


class Province(APIView):

    def get(self, request):
        params = request.query_params.dict()
        json_data = {
            "code": 0,
            "data": [
                {
                    "firstLetter": "b",
                    "id": "110000000000",
                    "jianpin": "bjs",
                    "level": 1,
                    "name": "北京市",
                    "nameEn": "Beijing",
                    "pinyin": "beijingshi"
                },
                {
                    "firstLetter": "z",
                    "id": "330000000000",
                    "jianpin": "zjs",
                    "level": 1,
                    "name": "浙江省",
                    "nameEn": "Zhejiang",
                    "pinyin": "zhejiangsheng"
                }
            ],
            "msg": "success"
        }
        return Response(json_data)


class ProvinceChild(APIView):

    def get(self, request):
        params = request.query_params.dict()
        json_data = {
            "code": 0,
            "data": [
                {
                    "firstLetter": "h",
                    "id": "330100000000",
                    "jianpin": "hzs",
                    "level": 2,
                    "name": "杭州市",
                    "nameEn": "Hangzhou",
                    "pid": "330000000000",
                    "pinyin": "hangzhoushi"
                },
                {
                    "firstLetter": "n",
                    "id": "330200000000",
                    "jianpin": "nbs",
                    "level": 2,
                    "name": "宁波市",
                    "nameEn": "Ningbo",
                    "pid": "330000000000",
                    "pinyin": "ningboshi"
                }
            ],
            "msg": "success"
        }
        return Response(json_data)


class UserDetail(APIView):

    def get(self, request):
        params = request.query_params.dict()
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')

        json_data = {
            "code": 0,
            "data": {
                "ext": {},
                "userLevel": {
                    "dateAdd": "2020-03-27 10:47:42",
                    "dateUpdate": "2021-01-19 22:21:19",
                    "defValidityUnit": 3,
                    "id": 1815,
                    "level": 0,
                    "name": "测试会员",
                    "paixu": 0,
                    "rebate": 10,
                    "status": 0,
                    "upgradePayNumber": 0,
                    "upgradeScore": 0,
                    "userId": 951
                },
                "saleDistributionTeam": {
                    "curSaleroom": 0,
                    "dateAdd": "2021-05-17 17:50:06",
                    "days": 30,
                    "leader": 1351478,
                    "name": "gooking（api工厂创始人）的团队",
                    "p1": 10,
                    "p2": 0,
                    "reportMonth": "20211213",
                    "standardSaleroom": 10000,
                    "tkAmount": 0
                },
                "base": {
                    "avatarUrl": "https://dcdn.it120.cc/cuser/951/2021/07/15/309311d6-52a3-46a4-931c-6458aff42f58.jpg",
                    "birthday": "1990-07-14",
                    "birthdayProcessSuccessYear": 2021,
                    "city": "Hangzhou",
                    "dateAdd": "2020-04-17 13:44:29",
                    "dateLogin": "2021-12-14 16:48:51",
                    "gender": 2,
                    "getLevelDate": "2021-06-25 17:05:25",
                    "id": 1351478,
                    "ipAdd": "127.0.0.1",
                    "ipLogin": "1.2.3.4",
                    "isFaceCheck": False,
                    "isIdcardCheck": False,
                    "isSeller": True,
                    "isTeamLeader": False,
                    "isTeamMember": False,
                    "lastOrderDate": "2021-12-05 10:14:16",
                    "levelId": 1815,
                    "levelRenew": False,
                    "mobile": "13500000000",
                    "mobileVisInvister": True,
                    "nick": "gooking（api工厂创始人）",
                    "province": "Zhejiang",
                    "pwd": "yes",
                    "pwdPay": "yes",
                    "referrerType": 0,
                    "sellerLevelId": 3,
                    "source": 0,
                    "sourceStr": "小程序",
                    "status": 0,
                    "statusStr": "默认",
                    "taskUserLevelSendMonth": 202112,
                    "taskUserLevelSendPerMonth": False,
                    "taskUserLevelUpgrade": False,
                    "teamId": 36,
                    "username": "gooking"
                }
            },
            "msg": "success"
        }
        return Response(json_data)


class CardMy(APIView):
    """我的会员卡"""

    def get(self, request):
        params = request.query_params.dict()
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')

        json_data = {
            "code": 0,
            "data": {},
            "msg": "success"
        }
        return Response(json_data)


class UserAmount(APIView):
    """查看用户资产"""

    def get(self, request):
        params = request.query_params.dict()
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')

        json_data = {
            "code": 0,
            "data": {},
            "msg": "success"
        }
        return Response(json_data)


class OrderCreate(APIView):

    def post(self, request):
        params = request.data
        conditions = {
            'userId': wx_utils.get_openid(params.get('token')),
            'calculate': True if params.get('calculate') in ('false', 'true') else False,
            'cardId': params.get('cardId'),
            'cityId': params.get('cityId'),
            'couponId': params.get('couponId'),
            'deductionScore': params.get('deductionScore'),
            'districtId': params.get('districtId'),
            'goodsJsonStr': params.get('goodsJsonStr', []),
            'goodsType': params.get('goodsType'),
            'peisongType': params.get('peisongType'),
            'provinceId': params.get('provinceId'),
            'remark': params.get('remark'),
            'address': params.get('address'),
            'extJsonStr': params.get('extJsonStr', {}),
            'linkMan': params.get('linkMan'),
            'mobile': params.get('mobile'),
        }

        mo.Order.objects.create(**conditions)

        json_data = {
            "code": 0,
            "data": {},
            "msg": "success"
        }
        return Response(json_data)


class OrderList(APIView):

    def post(self, request):
        params = request.data
        open_id = wx_utils.get_openid(params.get('token'))
        key = params.get('key')
        json_data = {
            "code": 0,
            "data": {
                "totalRow": 40,
                "logisticsMap": {
                    "1238758": {
                        "address": "快递详细收货地址",
                        "areaStr": "西湖区",
                        "cityId": "330100000000",
                        "cityStr": "杭州市",
                        "districtId": "330106000000",
                        "id": 1238758,
                        "linkMan": "张三",
                        "mobile": "13500000000",
                        "provinceId": "330000000000",
                        "provinceStr": "浙江省",
                        "status": -1,
                        "streetId": "330106109000",
                        "type": 0
                    }
                },
                "totalPage": 40,
                "orderList": [
                    {
                        "amount": 189,
                        "amountCard": 0,
                        "amountCoupons": 0,
                        "amountLogistics": 0,
                        "amountReal": 189,
                        "amountRefundTotal": 0,
                        "amountTax": 0,
                        "amountTaxGst": 0,
                        "amountTaxService": 0,
                        "autoDeliverStatus": 0,
                        "dateAdd": "2021-12-10 14:09:50",
                        "dateClose": "2021-12-10 14:20:50",
                        "dateUpdate": "2021-12-10 14:21:10",
                        "differHours": 101,
                        "goodsNumber": 1,
                        "hasRefund": False,
                        "id": 1238758,
                        "ip": "1.2.3.4",
                        "isCanHx": False,
                        "isDelUser": False,
                        "isEnd": False,
                        "isHasBenefit": False,
                        "isNeedLogistics": True,
                        "isPay": False,
                        "isScoreOrder": True,
                        "isSuccessPingtuan": False,
                        "jd8Status": 0,
                        "orderNumber": "21121014099510005",
                        "orderType": 0,
                        "periodAutoPay": False,
                        "pid": 0,
                        "qudanhao": "0005",
                        "refundStatus": 0,
                        "remark": "",
                        "score": 1,
                        "scoreDeduction": 0,
                        "shopId": 0,
                        "status": -1,
                        "statusStr": "订单关闭",
                        "trips": 0,
                        "type": 0,
                        "uid": 1351478,
                        "userId": 951
                    }
                ],
                "goodsMap": {
                    "1238758": [
                        {
                            "afterSale": "0,1,2",
                            "amount": 189,
                            "amountCoupon": 0,
                            "amountSingle": 189,
                            "amountSingleBase": 189,
                            "barCode": "a0000000001",
                            "buyRewardEnd": False,
                            "categoryId": 1872,
                            "cyTableStatus": 0,
                            "dateAdd": "2021-12-10 14:09:50",
                            "fxType": 2,
                            "goodsId": 4232,
                            "goodsName": "兔毛马甲",
                            "goodsSubName": "bieming",
                            "id": 1956214,
                            "isProcessHis": True,
                            "isScoreOrder": True,
                            "number": 1,
                            "numberNoFahuo": 1,
                            "orderId": 1238758,
                            "pic": "https://cdn.it120.cc/apifactory/2019/06/25/76d3c433-96ea-4f41-b149-31ea0983cd8f.jpg",
                            "propertyChildIds": "",
                            "purchase": False,
                            "refundStatus": 0,
                            "saleDateEnd": "2021-12-21 09:58:28",
                            "score": 1,
                            "shopId": 0,
                            "status": -1,
                            "type": 0,
                            "uid": 1351478,
                            "unit": "份",
                            "userId": 951
                        }
                    ]
                }
            },
            "msg": "success"
        }
        return Response(json_data)


class SubShopList(APIView):

    def post(self, request):
        json_data = {
            "code": 0,
            "data": [
                {
                    "address": "成都市天府新区-天目中心-家鑫超市",
                    "cityId": "330100000000",
                    "cyTablePayMod": 1,
                    "dateAdd": "2020-02-20 14:42:12",
                    "dateUpdate": "2021-04-09 17:16:38",
                    "districtId": "330106000000",
                    "goodsNeedCheck": False,
                    "id": 6041,
                    "latitude": 30.29966,
                    "linkMan": "雍正",
                    "linkPhone": "057118182512",
                    "longitude": 120.107697,
                    "name": "成都市天府新区",
                    "numberGoodReputation": 0,
                    "numberOrder": 0,
                    "openScan": True,
                    "openWaimai": True,
                    "openZiqu": True,
                    "openingHours": "8:30AM ~ 10:30PM",
                    "paixu": 0,
                    "provinceId": "330000000000",
                    "status": 1,
                    "statusStr": "正常",
                    "taxGst": 0,
                    "taxService": 0,
                    "userId": 951
                }
            ],
            "msg": "success"
        }
        return Response(json_data)


class BindMobile(APIView):

    def post(self, request):
        """
        {
            'token': 'gAAAAABh7hPzR0vBfJdYe_aqLV5L-Kty7eaoPbFqPWwHTxJgg93pVBapRn02_33TKQKjkaeFg4pB89S1G3iqrCI-KrW9pqaGvH9RHo9O19ZuPcPg4akiEnU=',
            'code': '033ASjGa1vfrwC0BXlIa1xbEyc0ASjG-',
            'encryptedData': '0rPXQXFJfzhG7kQnmxjBr5Xsu6Vm0emy8r10LmioYZ1XWfXbTJpDGuXiJZgn7xF4qTbU+1pWc6qE2KMA2H2bJgRxsPOG0Q/1XkBfQ6uV0eFs46a03J+RUWapAc2dqVrgAHyPihJpWcBiNJ9t+CbBov+qCeyGfijDrDc7pKrurEjCtOtU9UOfGIhFr5P3d0gEZ340Mnb3tytEMg7xLWGQIg==',
            'iv': 'b6rL5+MSnQaOdHtRohdMug==', 'pwd': ''
        }
        """
        r = wx_utils.Wx3rdSession()
        json_data = {
            "code": 0,
            "data": {'linkPhone': '110'},
            "msg": "success"
        }
        return Response(json_data)

import json

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from app import models as mo
from app.paginations import NoticeListPagination
from app import serializers as se
from utils import wx_utils, exception_utils


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

        obj = wx_utils.Wx3rdSession(openid, session_key)
        session = obj.get_3rd_session()
        json_data = {
            "code": 0,
            "msg": "success",
            'data': {'token': session, 'uid': openid}
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
            query_set = query_set.filter(categoryId=category_id)
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
        params = request.query_params.dict()
        query_set = mo.SiteGoodsDynamic.objects.filter().all()
        serializer = se.SiteGoodsDynamicSerializer(query_set, many=True)
        json_data = {
            "code": 0,
            "data": {
                "number": 100,  # 购物车商品总数量
                "score": 0,   # 需要消耗的积分
                "shopList": [    # 门店列表 默认0
                    {
                        "id": 0,
                        "name": "",
                        "serviceDistance": 99999999
                    }
                ],
                "goodsStatus": [  # 商品的状态

                ],
                "price": 848,  # 结算总价
                "items": [
                    {
                        "key": "5b2a16e8d15d25b416e87f228b6d50f3",  # 购物车记录唯一编号
                        "goodsId": 810285,  # 商品ID
                        "number": 1,        # 商品数量
                        "sku": [
                            {
                                "optionId": 30899,
                                "optionValueId": 320215,
                                "optionName": "网络类型",
                                "optionValueName": "WIFI"
                            },
                            {
                                "optionId": 30900,
                                "optionValueId": 320217,
                                "optionName": "新订单提示",
                                "optionValueName": "滴滴声"
                            },
                            {
                                "optionId": 30901,
                                "optionValueId": 320220,
                                "optionName": "切纸方式",
                                "optionValueName": "手动撕纸"
                            }
                        ],
                        "additions": [
                            {
                                "id": 2833,
                                "name": "自己对接",
                                "pid": 852,
                                "pname": "对接方式",
                                "price": 0
                            }
                        ],
                        "categoryId": 1875,  # 类目ID
                        "shopId": 0,  # 门店ID
                        "score": 0,
                        "pic": "https:#dcdn.it120.cc/2020/04/15/0a86e7ef-3680-4f9f-a22c-2afb26672b7d.png",
                        "name": "小票打印机工厂定制版",
                        "minBuyNumber": 1,  # 至少需要购买几件
                        "weight": 0,
                        "logisticsId": 386,
                        "price": 299,
                        "selected": True,  # 是否选中
                        "stores": 999969,  # 剩余库存
                        "status": 0,
                        "statusStr": "上架"
                    },
                    {
                        "key": "d27a3ad5b78ad3edb4f51b6b23de7a07",
                        "goodsId": 435060,
                        "number": 1,
                        "additions": [
                            {
                                "id": 41,
                                "name": "自己对接",
                                "pid": 24,
                                "pname": "对接服务",
                                "price": 0
                            }
                        ],
                        "categoryId": 1875,
                        "shopId": 0,
                        "score": 0,
                        "pic": "https:#dcdn.it120.cc/2020/05/22/83618213-99b6-42ce-a672-becf466aa515.png",
                        "name": "WiFi云标签机 FP-N20W",
                        "minBuyNumber": 1,
                        "weight": 0,
                        "logisticsId": 386,
                        "price": 499,
                        "selected": True,
                        "stores": 9983,
                        "status": 0,
                        "statusStr": "上架"
                    },
                    {
                        "key": "2096702b2b8b596ef5a4950e26be5085",
                        "goodsId": 235853,
                        "number": 1,
                        "sku": [
                            {
                                "optionId": 869,
                                "optionValueId": 1698,
                                "optionName": "花色",
                                "optionValueName": "粉色叶子"
                            },
                            {
                                "optionId": 871,
                                "optionValueId": 1588,
                                "optionName": "颜色",
                                "optionValueName": "红色"
                            }
                        ],
                        "categoryId": 1875,
                        "shopId": 0,
                        "score": 0,
                        "pic": "https:#dcdn.it120.cc/2019/12/06/ebf49ac6-4521-4bcc-92fd-8bbbd4131167.jpg",
                        "name": "3分钟沙漏「儿童刷牙计时器」",
                        "subName": "别名啦啦啦",
                        "minBuyNumber": 1,
                        "weight": 1.5,
                        "logisticsId": 51089,
                        "price": 50,
                        "selected": True,
                        "stores": 9989,
                        "status": 0,
                        "statusStr": "上架"
                    }
                ]
            },
            "msg": "success"
        }
        return Response(json_data)


class ShopCartGoodsUpdate(APIView):
    """获取购物车信息"""

    def post(self, request):
        params = request.query_params.dict()
        query_set = mo.SiteGoodsDynamic.objects.filter().all()
        serializer = se.SiteGoodsDynamicSerializer(query_set, many=True)
        json_data = {
            "code": 0,
            "data": {},
            "msg": "success"
        }
        return Response(json_data)


class ShopCartGoodsRemove(APIView):
    """获取购物车信息"""

    def post(self, request):
        params = request.query_params.dict()
        query_set = mo.SiteGoodsDynamic.objects.filter().all()
        serializer = se.SiteGoodsDynamicSerializer(query_set, many=True)
        json_data = {
            "code": 0,
            "data": {},
            "msg": "success"
        }
        return Response(json_data)
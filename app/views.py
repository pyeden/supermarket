import json
import re
import time

import requests
from cryptography.fernet import Fernet
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, InvalidPage
from django.http import JsonResponse, Http404
from haystack.forms import ModelSearchForm
from haystack.generic_views import RESULTS_PER_PAGE
from haystack.query import EmptySearchQuerySet
from haystack.views import SearchView
from rest_framework import viewsets, mixins
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


class HaystackSearch(SearchView):

    def __init__(self):
        super(HaystackSearch, self).__init__()

    def build_form(self, form_kwargs=None):
        """
        Instantiates the form the class should use to process the search query.
        """
        data = None
        kwargs = {"load_all": self.load_all}
        if form_kwargs:
            kwargs.update(form_kwargs)

        if self.request.method == 'POST':
            try:
                prams = json.loads(self.request.body.decode())
                data = {
                    'q': prams.pop('k')
                }
            except Exception as e:
                print(e)

        if self.searchqueryset is not None:
            kwargs["searchqueryset"] = self.searchqueryset

        return self.form_class(data, **kwargs)

    def build_page(self):
        try:
            prams = json.loads(self.request.body.decode())
            page_no = int(prams.get("page", 1))
        except (TypeError, ValueError):
            raise Http404("Not a valid number for page.")

        if page_no < 1:
            raise Http404("Pages should be 1 or greater.")
        paginator = Paginator(self.results, self.results_per_page)
        try:
            page = paginator.page(page_no)
        except InvalidPage:
            raise Http404("No such page!")
        return paginator, page

    def create_response(self):

        context = self.get_context()
        json_data = []
        for result in (item.object for item in context['page'].object_list):
            json_data.append(se.GoodsSerializer(result).data)
        result = {"code": 0, "msg": 'Search successfully！', "data": {'result': json_data}}
        return JsonResponse(result)


def basic_search(
        request,
        load_all=True,
        form_class=ModelSearchForm,
        searchqueryset=None,
        extra_context=None,
        results_per_page=None
):
    """
    """
    query = ""
    results = EmptySearchQuerySet()

    prams = json.loads(request.body.decode())
    query_data = {
        'q': prams.pop('k')
    }
    if query_data:
        form = form_class(query_data, searchqueryset=searchqueryset, load_all=load_all)

        if form.is_valid():
            query = form.cleaned_data["q"]
            results = form.search()
    else:
        form = form_class(searchqueryset=searchqueryset, load_all=load_all)

    paginator = Paginator(results, results_per_page or RESULTS_PER_PAGE)

    try:
        page = paginator.page(int(prams.get("page", 1)))
    except InvalidPage:
        raise Http404("No such page of results!")

    context = {
        "form": form,
        "page": page,
        "paginator": paginator,
        "query": query,
        "suggestion": None,
    }

    if results.query.backend.include_spelling:
        context["suggestion"] = form.get_suggestion()

    if extra_context:
        context.update(extra_context)

    json_data = []
    for result in (item.object for item in page.object_list):
        json_data.append(se.GoodsSerializer(result).data)
    result = {"code": 0, "msg": 'Search successfully！', "data": {'result': json_data}}
    return JsonResponse(result)


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
        # recommend_status = params.get('recommendStatus')
        # miao_sha = params.get('miaosha')
        query_set = mo.Goods.objects.all()
        if category_id:
            query_set = query_set.filter(category_id=category_id)
        # if recommend_status:
        #     query_set = query_set.filter(recommendStatus=recommend_status)
        # if miao_sha:
        #     query_set = query_set.filter(miaosha=miao_sha)

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
    """删除购物车商品"""

    def post(self, request):
        params = request.data
        open_id = wx_utils.get_openid(params.get('token'))
        keys = params.get('key')
        key_list = keys.split(',') if keys else []
        goods = mo.ShopCart.objects.filter(user_id=open_id).filter(key__in=key_list).first()
        if goods:
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
        open_id = wx_utils.get_openid(params.pop('token'))
        query_set = mo.Address.objects.filter(userId=open_id).filter(isDefault=True).first()
        serializer = se.AddressSerializer(query_set)

        json_data = {
            "code": 0,
            "data": {
                "extJson": {},
                "info": serializer.data
            },
            "msg": "success"
        }
        return Response(json_data)


class ShopAddressList(APIView):

    def get(self, request):
        params = request.query_params.dict()
        open_id = wx_utils.get_openid(params.pop('token'))
        key = params.get('key')
        query_set = mo.Address.objects.filter(userId=open_id).all()
        serializer = se.AddressSerializer(query_set, many=True)

        json_data = {
            "code": 0,
            "data": serializer.data,
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
        user_id = wx_utils.get_openid(params.pop('token'))
        params.update({
            'userId': user_id
        })

        params = common_utils.parse_data(params)

        mo.Address.objects.create(**params)

        json_data = {
            "code": 0,
            "data": {},
            "msg": "success"
        }
        return Response(json_data)


class ShopAddressUpdate(APIView):

    def post(self, request):
        params = request.data
        open_id = wx_utils.get_openid(params.pop('token'))
        address_id = params.get('id')
        default_address = mo.Address.objects.filter(userId=open_id).filter(isDefault=True).first()
        if default_address:
            default_address.isDefault = False
            default_address.save()
        address = mo.Address.objects.filter(userId=open_id).filter(id=address_id).first()
        if address:
            address.isDefault = True
            address.save()

        query_set = mo.Address.objects.filter(userId=open_id).first()
        serializer = se.AddressSerializer(query_set)
        json_data = {
            "code": 0,
            "data": {
                "extJson": {},
                "info": serializer.data
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
                    "firstLetter": "s",
                    "id": '1000',
                    "jianpin": "sc",
                    "level": 1,
                    "name": "四川省",
                    "nameEn": "SiChuan",
                    "pinyin": "sichuansheng"
                },
            ],
            "msg": "success"
        }
        return Response(json_data)


class City(APIView):

    def get(self, request):
        params = request.query_params.dict()
        json_data = {
            "code": 0,
            "data": [
                {
                    "firstLetter": "c",
                    "id": '2000',
                    "jianpin": "sc",
                    "level": 2,
                    "name": "成都市",
                    "nameEn": "ChengDu",
                    "pid": "1000",
                    "pinyin": "chengdushi"
                },
            ],
            "msg": "success"
        }
        return Response(json_data)


class Districts(APIView):

    def get(self, request):
        params = request.query_params.dict()
        json_data = {
            "code": 0,
            "data": [
                {
                    "firstLetter": "t",
                    "id": '3000',
                    "jianpin": "tfxq",
                    "level": 3,
                    "name": "天府新区",
                    "pid": "2000",
                    "nameEn": "TianFuXinQu",
                    "pinyin": "tianfuxinqu"
                },
            ],
            "msg": "success"
        }
        return Response(json_data)


class Streets(APIView):

    def get(self, request):
        params = request.query_params.dict()
        json_data = {
            "code": 0,
            "data": [
                {
                    "firstLetter": "s",
                    "id": '4000',
                    "jianpin": "sc",
                    "level": 4,
                    "name": "天目中心",
                    "pid": "3000",
                    "nameEn": "TianMuZhongXin",
                    "pinyin": "tianmuzhongxin"
                },
            ],
            "msg": "success"
        }
        return Response(json_data)


class ProvinceChild(APIView):

    def get(self, request):
        params = request.query_params.dict()
        pid = params.get('pid')
        data = {
            '1000': [
                {
                    "firstLetter": "c",
                    "id": '2000',
                    "jianpin": "cd",
                    "level": 2,
                    "name": "成都市",
                    "nameEn": "ChengDu",
                    "pid": '1000',
                    "pinyin": "hangzhoushi"
                },
            ],
            '2000': [
                {
                    "firstLetter": "t",
                    "id": '3000',
                    "jianpin": "tfxq",
                    "level": 3,
                    "name": "天府新区",
                    "pid": "2000",
                    "nameEn": "TianFuXinQu",
                    "pinyin": "tianfuxinqu"
                },
            ],
            '3000': [
                {
                    "firstLetter": "s",
                    "id": '4000',
                    "jianpin": "sc",
                    "level": 4,
                    "name": "天目中心",
                    "pid": "3000",
                    "nameEn": "TianMuZhongXin",
                    "pinyin": "tianmuzhongxin"
                },
            ],
        }
        json_data = {
            "code": 0,
            "data": data[pid],
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
        user_id = wx_utils.get_openid(params.pop('token'))
        params = common_utils.parse_data(params)

        goods_infos = params.get('goodsJsonStr')
        total_prices = 0
        goods_numbers = 0
        for goods in json.loads(goods_infos):
            goods_number = goods.get('number', 0)
            goods_price = goods.get('price', 0)
            total_price = goods_price * goods_number
            total_prices += total_price
            goods_numbers += goods_number

        if not params.get('calculate'):
            # 真实下单是没有calculate字段
            params.update({
                'userId': user_id,
                'orderNumber': str(int(time.time()*1000)),
                'payPrices': total_prices,
                'amountReal': total_prices,
                'goodsNumber': goods_numbers,
            })
            mo.Order.objects.create(**params)
            json_data = {
                "code": 0,
                "data": {},
                "msg": "success"
            }
        else:
            # 预下单
            json_data = {
                "code": 0,
                "data": {
                    "amountReal": total_prices,
                    "isNeedLogistics": True,   # 选择配送方式
                    "goodsNumber": goods_numbers,
                },
                "msg": "success"
            }
        return Response(json_data)


class OrderList(APIView):

    def post(self, request):
        params = request.data
        user_id = wx_utils.get_openid(params.get('token'))
        status = params.get('key')
        query_set = mo.Order.objects.filter(userId=user_id)
        if status in (0, 1, 2, 3):
            query_set = query_set.filter(status=status).all()
        else:
            query_set = query_set.all()

        pg = NoticeListPagination()
        page_data = pg.paginate_queryset(queryset=query_set, request=request, view=self)
        serializer = se.OrderSerializer(page_data, many=True)

        goods_map = {}
        for order in serializer.data:
            goods_list = json.loads(order.get('goodsJsonStr'))
            goods_map[order.get('id')] = goods_list
        json_data = {
            "code": 0,
            "data": {
                "totalRow": pg.page.paginator.count,
                "logisticsMap": goods_map,
                "totalPage": pg.page.paginator.num_pages,
                "orderList": serializer.data,
                "goodsMap": goods_map
            },
            "msg": "success"
        }
        return Response(json_data)


class OrderStatistic(APIView):
    """统计订单信息"""

    def get(self, request):
        params = request.query_params.dict()
        user_id = wx_utils.get_openid(params.pop('token'))
        order_id = params.get('id')

        return Response({
            "code": 0,
            "data": {},
            'msg': 'success'
        })


class OrderDetail(APIView):
    """订单详情"""

    def get(self, request):
        params = request.query_params.dict()
        user_id = wx_utils.get_openid(params.pop('token'))
        order_id = params.get('id')

        query_set = mo.Order.objects.filter(userId=user_id).filter(id=order_id).first()
        seriallizer = se.OrderSerializer(query_set)

        order = seriallizer.data
        goods_list = json.loads(order.get('goodsJsonStr'))

        json_data = {
            "code": 0,
            "data": {
                "orderInfo": order,
                "goods": goods_list,
                "logistics": order,
            },
            "msg": "success"
        }
        return Response(json_data)


class SubShopList(APIView):
    """配置超市地址"""

    def post(self, request):

        query_set = mo.ShopAddress.objects.all()
        serializer = se.ShopAddressSerializer(query_set, many=True)

        json_data = {
            "code": 0,
            "data": serializer.data,
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
        code = request.data.get('code')
        res = wx_utils.get_wx_auth_session(code)
        session_key = res.get('session_key')
        pc = wx_utils.WXBizDataCrypt('wxad795e910e81f909', session_key)

        s = pc.decrypt(request.data.get('encryptedData'), request.data.get('iv'))
        json_data = {
            "code": 0,
            "data": s.get('phoneNumber'),
            "msg": "success"
        }
        return Response(json_data)


class PayWxWxapp(APIView):

    def post(self, request):
        params = common_utils.parse_data(request.data)
        user_id = wx_utils.get_openid(params.pop('token'))
        params.update({
            'openid': user_id
        })

        res = requests.post('https://api.mch.weixin.qq.com/pay/unifiedorder', data=params)
        json_data = {
            "code": 0,
            "data": {
                "timeStamp": "1639301968360",
                "outTradeId": "ZF2112122009197309",
                "package": "prepay_id=wx121739282777950d4a4f7f0af016300000",
                "paySign": "E3BD35F75CC02825F269D78B7BD6526E",
                "appid": "wxa46b09d413fbcaff",
                "sign": "E3BD35F75CC02825F269D78B7BD6526E",
                "signType": "MD5",
                "prepayId": "wx121739282777950d4a4f7f0af016300000",
                "nonceStr": "DJe3ZmjvsJPBiVLgLY18OUjbUZ7lTk"
            },
            "msg": "success"
        }
        return Response(json_data)

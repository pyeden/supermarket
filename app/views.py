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
            "data": {'number': 4},
            "msg": "success"
        }
        return Response(json_data)
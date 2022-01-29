"""supermarket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import routers

from app import views


urlpatterns = [
    path('api/v1/config/values', views.ConfigList.as_view(), name='configs'),
    # 小程序用户授权，自动注册并登录
    path('api/v1/user/wxapp/authorize', views.WxAppAuthorize.as_view(), name='authorize'),
    path('api/v1/user/check-token', views.CheckToken.as_view(), name='authorize'),

    path('api/v1/shop/goods/list', views.ShopGoodsList.as_view(), name='goods_list'),
    path('api/v1/shop/goods/detail', views.ShopGoodsDetail.as_view(), name='goods_detail'),
    path('api/v1/user/wxapp/login', views.WxAppLogin.as_view(), name='login'),
    path('api/v1/shop/goods/category/all', views.CategoryAll.as_view(), name='category'),
    path('api/v1/banner/list', views.BannerList.as_view(), name='banners'),
    path('api/v1/notice/list', views.NoticeList.as_view(), name='notices'),
    path('api/v1/site/adPosition/info', views.SiteAdPositionInfo.as_view(), name='position_info'),
    path('api/v1/site/goods/dynamic', views.SiteGoodsDynamic.as_view(), name='goods_dynamic'),

    path('api/v1/shopping-cart/info', views.ShopCart.as_view(), name='car_goods'),
    path('api/v1/shopping-cart/add', views.ShopCartGoodsAdd.as_view(), name='car_goods_add'),
    path('api/v1/shopping-cart/modifyNumber', views.ShopCartGoodsUpdate.as_view(), name='car_goods_modify'),
    path('api/v1/shopping-cart/remove', views.ShopCartGoodsRemove.as_view(), name='car_goods_remove'),

    path('api/v1/user/detail', views.UserDetail.as_view(), name='user_detail'),
    path('api/v1/card/my', views.CardMy.as_view(), name='card_my'),
    path('api/v1/user/amount', views.UserAmount.as_view(), name='user_amount'),

    path('api/v1/shop/subshop/list', views.SubShopList.as_view(), name='sub_shop_list'),
    path('api/v1/user/wxapp/bindMobile', views.BindMobile.as_view(), name='bind_mobile'),

    path('api/v1/user/shipping-address/default/v2', views.DefaultShopAddress.as_view(), name='address_default'),
    path('api/v1/user/shipping-address/list', views.ShopAddressList.as_view(), name='address_list'),
    path('api/v1/user/shipping-address/detail/v2', views.ShopAddressDetail.as_view(), name='address_detail'),
    path('api/v1/user/shipping-address/add', views.ShopAddressAdd.as_view(), name='address_add'),
    path('api/v1/user/shipping-address/update', views.ShopAddressUpdate.as_view(), name='address_update'),

    path('common/region/v2/province', views.Province.as_view(), name='province'),
    path('common/region/v2/city', views.City.as_view(), name='city'),
    path('common/region/v2/districts', views.Districts.as_view(), name='districts'),
    path('common/region/v2/streets', views.Streets.as_view(), name='streets'),
    path('common/region/v2/child', views.ProvinceChild.as_view(), name='province_child'),

    path('api/v1/order/list', views.OrderList.as_view(), name='order_list'),
    path('api/v1/order/create', views.OrderCreate.as_view(), name='order_create'),
    path('api/v1/order/detail', views.OrderDetail.as_view(), name='order_detail'),
    path('api/v1/order/statistics', views.OrderStatistic.as_view(), name='order_statistic'),

    path('api/v1/pay/wx/wxapp', views.PayWxWxapp.as_view(), name='order_detail'),
]

# router = routers.DefaultRouter()
router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns += router.urls

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
    path('config/values/', views.ConfigList.as_view(), name='configs'),
    path('user/wxapp/authorize/', views.WxAppAuthorize.as_view(), name='authorize'),
    path('banner/list/', views.BannerList.as_view(), name='banners'),
    path('shop/goods/category/all/', views.CategoryAll.as_view(), name='category'),
    path('shop/goods/list/', views.ShopGoodsList.as_view(), name='shop_goods'),
    path('discounts/coupons/', views.DiscountsCoupons.as_view(), name='discount_coupons'),
    path('notice/list/', views.NoticeList.as_view(), name='notices'),
    path('wx/live/rooms/', views.WxLiveRooms.as_view(), name='rooms'),
    path('site/adPosition/info/', views.SiteAdPositionInfo.as_view(), name='position_info'),
    path('site/goods/dynamic/', views.SiteGoodsDynamic.as_view(), name='goods_dynamic'),
    path('shop/goods/kanjia/set/v2/', views.ShopGoodsKanJiaSetV2.as_view(), name='goods_kan_jia_set'),

]

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'tests', views.TestViewSet)

urlpatterns += router.urls

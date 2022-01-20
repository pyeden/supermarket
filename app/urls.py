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
    path('config/values', views.ConfigList.as_view(), name='configs'),
    # 小程序用户授权，自动注册并登录
    path('user/wxapp/authorize', views.WxAppAuthorize.as_view(), name='authorize'),
    path('user/check-token', views.CheckToken.as_view(), name='authorize'),

    path('shop/goods/list', views.ShopGoodsList.as_view(), name='goods'),
    path('uuser/wxapp/login', views.WxAppLogin.as_view(), name='login'),
    path('shop/goods/category/all', views.CategoryAll.as_view(), name='category'),
    path('banner/list', views.BannerList.as_view(), name='banners'),
    path('notice/list', views.NoticeList.as_view(), name='notices'),
    path('site/adPosition/info', views.SiteAdPositionInfo.as_view(), name='position_info'),
    path('site/goods/dynamic', views.SiteGoodsDynamic.as_view(), name='goods_dynamic'),

    path('shopping-cart/info', views.ShopCart.as_view(), name='goods_dynamic'),

]

# router = routers.DefaultRouter()
router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns += router.urls

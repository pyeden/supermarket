from django.contrib.auth.models import User, Group
from rest_framework import serializers

from app import models as m


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Goods
        fields = '__all__'


class BannersSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Banner
        fields = '__all__'


# class NoticeSerializer(serializers.Serializer):
class NoticeSerializer(serializers.ModelSerializer):
    """序列化"""

    class Meta:
        model = m.Notice
        fields = '__all__'


class GoodsCategorySerializer(serializers.ModelSerializer):
    """序列化"""

    class Meta:
        model = m.GoodsCategory
        fields = '__all__'


class HomeAdvertisingSerializer(serializers.ModelSerializer):
    """序列化"""

    class Meta:
        model = m.HomeAdvertising
        fields = '__all__'


class SiteGoodsDynamicSerializer(serializers.ModelSerializer):
    """序列化"""

    class Meta:
        model = m.SiteGoodsDynamic
        fields = '__all__'


class ConfigSerializer(serializers.ModelSerializer):
    """序列化"""

    class Meta:
        model = m.Config
        fields = '__all__'

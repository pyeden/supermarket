import time
import datetime
import warnings

from django.conf import settings
from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone
from django.db import models
from django.core import exceptions
from django.utils.dateparse import (
    parse_date, parse_datetime
)


class TimeStampField(models.DateTimeField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'FloatField'

    def get_db_prep_value(self, value, connection, prepared=False):
        # Casts datetimes into the format expected by the backend
        if not prepared:
            value = self.get_prep_value(value)
        return value

    def get_prep_value(self, value):
        """Perform preliminary non-db specific value checks and conversions."""
        if value is None:
            return value
        return self.to_python(value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return datetime.datetime.fromtimestamp(value)
        except TypeError as e:
            print('eeeeeeee', e)
            return datetime.datetime.fromtimestamp(int(value))

    def to_python(self, value):
        if value is None or isinstance(value, float) or value == 0:
            return value
        if isinstance(value, datetime.datetime):
            return value.timestamp()
        if isinstance(value, datetime.date):
            value = datetime.datetime(value.year, value.month, value.day)
            if settings.USE_TZ:
                # For backwards compatibility, interpret naive datetimes in
                # local time. This won't work during DST change, but we can't
                # do much about it, so we let the exceptions percolate up the
                # call stack.
                warnings.warn("DateTimeField %s.%s received a naive datetime "
                              "(%s) while time zone support is active." %
                              (self.model.__name__, self.name, value),
                              RuntimeWarning)
                default_timezone = timezone.get_default_timezone()
                value = timezone.make_aware(value, default_timezone)
            return value.timestamp()

        try:
            parsed = parse_datetime(value)
            if parsed is not None:
                return parsed.timestamp()
        except ValueError:
            raise exceptions.ValidationError(
                self.error_messages['invalid_datetime'],
                code='invalid_datetime',
                params={'value': value},
            )

        try:
            parsed = parse_date(value)
            if parsed is not None:
                value = datetime.datetime(parsed.year, parsed.month, parsed.day)
                return value.timestamp()
        except ValueError:
            raise exceptions.ValidationError(
                self.error_messages['invalid_date'],
                code='invalid_date',
                params={'value': value},
            )

        raise exceptions.ValidationError(
            self.error_messages['invalid'],
            code='invalid',
            params={'value': value},
        )


class BaseManager(models.Manager):
    """
    自定义管理器
    """

    def get_queryset(self):
        """
        过滤已经软删除的数据
        """
        # return super(BaseManager, self).get_queryset().filter(is_delete=1)
        return super(BaseManager, self).get_queryset()

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


IS_CHOICE = (
        (0, '否'),
        (1, '是')
    )

RECOMMEND = (
        (0, '普通'),
        (1, '推荐')
    )

PRODUCTION_STATUS = (
        (0, '下架'),
        (1, '上架')
    )

BOOL_CHOICE = (
    (True, '真'),
    (False, '假')
)


class BaseModel(models.Model):
    """
    自定义基类模型
    包含软删除的业务模型，都建议继承此模型
    """

    id = models.AutoField(primary_key=True)
    dateAdd = TimeStampField('创建时间', auto_now_add=True)
    dateUpdate = TimeStampField('更新时间', auto_now=True)
    dateDelete = TimeStampField('删除时间', null=True, blank=True, default=0)
    is_delete = models.BooleanField('是否删除', null=True, blank=True, choices=IS_CHOICE, default=0)

    objects = BaseManager()

    class Meta:
        """
        必须为抽象类
        """
        abstract = True
        ordering = ['-id']

    def delete(self, using=None, keep_parents=False):
        """
        重写父类删除方法，改为软删除
        """
        self.is_delete = 1
        self.delete_t = timezone.now()
        self.save()

    def delete_real(self, using=None, keep_parents=False):
        """
        真实删除
        """
        super().delete(using, keep_parents)

    def __str__(self):
        # if hasattr(self, 'name'):
        #     from django.apps import apps
        #     obj = apps.get_model(self._meta.app_label, self._meta.model_name)
        #     for field in obj._meta.fields:
        #         if field.name == self.name:
        #             return f"{field.verbose_name}_{self.name}"
        if hasattr(self, 'name'):
            return f"{self.name}"
        return f"{self.id}"


class GoodsCategory(BaseModel):
    """商品分类"""

    icon = models.CharField("图标", max_length=255, null=True, blank=True, default='0')
    key = models.CharField('标号', max_length=255, null=True, blank=True, default='0')
    name = models.CharField('名称', max_length=255, null=True, blank=True, default='0')
    type = models.CharField('类别', max_length=255, null=True, blank=True, default='0')
    level = models.IntegerField(null=True, blank=True, default=0)
    paixu = models.IntegerField(null=True, blank=True, default=0)
    pid = models.IntegerField(null=True, blank=True, default=0)
    shopId = models.IntegerField(null=True, blank=True, default=0)
    userId = models.IntegerField(null=True, blank=True, default=0)
    isUse = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=True)

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'


class Goods(BaseModel):
    """商品"""

    categoryId = models.ForeignKey(GoodsCategory, verbose_name='商品分类', on_delete=models.CASCADE, to_field="id", related_name='category_goods')
    number = models.IntegerField('库存', null=True, blank=True, default=0)
    dayDue = models.IntegerField('保质期（单位/月）', null=True, blank=True, default=0)
    dateProduction = TimeStampField('生产日期', null=True, blank=True, default=0)
    dateEndCountDown = TimeStampField('倒计时', null=True, blank=True, default=0)
    dateEndPingtuan = TimeStampField('拼团时间', null=True, blank=True, default=0)
    dateEnd = TimeStampField('结束时间', null=True, blank=True, default=0)
    afterSale = models.CharField(max_length=255, null=True, blank=True, default='0')
    characteristic = models.CharField('商品描述', max_length=255, null=True, blank=True, default='0')
    commission = models.FloatField(null=True, blank=True, default=0.0)
    commissionSettleType = models.IntegerField(null=True, blank=True, default=0)
    commissionType = models.IntegerField(null=True, blank=True, default=0)
    commissionUserType = models.IntegerField(null=True, blank=True, default=0)
    dateStart = TimeStampField('开始时间', null=True, blank=True, default=0)
    fxType = models.IntegerField(null=True, blank=True, default=0)
    gotScore = models.IntegerField(null=True, blank=True, default=0)
    gotScoreType = models.IntegerField(null=True, blank=True, default=0)
    hasAddition = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    hasTourJourney = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    hidden = models.IntegerField(null=True, blank=True, default=0)
    kanjia = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    kanjiaPrice = models.FloatField(null=True, blank=True, default=0)
    limitation = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    logisticsId = models.IntegerField(null=True, blank=True, default=0)
    maxCoupons = models.IntegerField(null=True, blank=True, default=0)
    miaosha = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    minBuyNumber = models.IntegerField(null=True, blank=True, default=0)
    minPrice = models.FloatField('最低价', null=True, blank=True, default=0)
    minScore = models.IntegerField(null=True, blank=True, default=0)
    name = models.CharField('商品名称', max_length=255, null=True, blank=True, default='0')
    numberFav = models.IntegerField(null=True, blank=True, default=0)
    numberGoodReputation = models.IntegerField(null=True, blank=True, default=0)
    numberOrders = models.IntegerField(null=True, blank=True, default=0)
    numberReputation = models.IntegerField(null=True, blank=True, default=0)
    numberSells = models.IntegerField(null=True, blank=True, default=0)
    originalPrice = models.FloatField('原价', null=True, blank=True, default=0)
    overseas = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    paixu = models.IntegerField(null=True, blank=True, default=0)
    pic = models.CharField('图片地址', max_length=255, null=True, blank=True, default='0')
    pingtuan = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    pingtuanPrice = models.FloatField(null=True, blank=True, default=0)
    recommendStatus = models.IntegerField('是否推荐商品', null=True, blank=True, choices=RECOMMEND, default=0)
    recommendStatusStr = models.CharField(max_length=255, null=True, blank=True, default='0')
    seckillBuyNumber = models.IntegerField(null=True, blank=True, default=0)
    sellEnd = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    sellStart = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=True)
    shopId = models.IntegerField(null=True, blank=True, default=0)
    status = models.IntegerField('商品状态', null=True, blank=True, choices=PRODUCTION_STATUS, default=1)
    statusStr = models.CharField(max_length=255, null=True, blank=True, default='0')
    storeAlert = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    stores = models.IntegerField(null=True, blank=True, default=0)
    stores0Unsale = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    type = models.IntegerField(null=True, blank=True, default=0)
    unusefulNumber = models.IntegerField(null=True, blank=True, default=0)
    usefulNumber = models.IntegerField(null=True, blank=True, default=0)
    userId = models.IntegerField(null=True, blank=True, default=0)
    vetStatus = models.IntegerField(null=True, blank=True, default=0)
    views = models.IntegerField(null=True, blank=True, default=0)
    weight = models.FloatField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = '商品列表'
        verbose_name_plural = '商品列表'

    # 控制显示长度
    def short_pic(self):
        if len(str(self.pic)) > 30:
            return '{}...'.format(str(self.pic)[0:29])
        else:
            return str(self.pic)

    short_pic.allow_tags = True
    short_pic.short_description = '商品图片地址'


class Config(BaseModel):
    """配置信息"""

    key = models.CharField("key", max_length=255, null=True, blank=True, default='0')
    remark = models.CharField("备注", max_length=255, null=True, blank=True, default='0')
    value = models.CharField("value", max_length=255, null=True, blank=True, default='0')

    class Meta:
        verbose_name = '小程序配置'
        verbose_name_plural = '小程序配置'


class Banner(BaseModel):
    """轮播图"""

    businessId = models.CharField("商户ID", max_length=255, null=True, blank=True, default='0')
    linkUrl = models.CharField("链接地址", max_length=255, null=True, blank=True, default='0')
    paixu = models.IntegerField(null=True, blank=True, default=0)
    picUrl = models.CharField("图片地址", max_length=255, null=True, blank=True, default='0')
    status = models.IntegerField(null=True, blank=True, default=0)
    statusStr = models.CharField(max_length=255, null=True, blank=True, default='0')
    title = models.CharField("标题", max_length=255, null=True, blank=True, default='0')
    type = models.CharField("类型", max_length=255, null=True, blank=True, default='0')
    userId = models.IntegerField("用户ID", null=True, blank=True, default=0)

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = '轮播图'


class Notice(BaseModel):
    """公告"""

    isShow = models.BooleanField('是否在首页显示', null=True, blank=True, choices=BOOL_CHOICE, default=True)
    title = models.TextField('标题', max_length=2048, null=True, blank=True, default='0')
    userId = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = '网站公告'
        verbose_name_plural = '网站公告'


class HomeAdvertising(BaseModel):
    """首页弹出广告"""

    name = models.CharField(max_length=255, null=True, blank=True, default='0')
    key = models.CharField(max_length=255, null=True, blank=True, default='0')
    type = models.CharField(max_length=255, null=True, blank=True, default='0')
    val = models.CharField(max_length=255, null=True, blank=True, default='0')

    class Meta:
        verbose_name = '弹窗广告'
        verbose_name_plural = '弹窗广告'


class SiteGoodsDynamic(BaseModel):
    """商品购买动态"""

    nick = models.CharField(max_length=255, null=True, blank=True, default='0')
    uid = models.IntegerField(null=True, blank=True, default=0)
    number = models.IntegerField(null=True, blank=True, default=0)
    orderId = models.IntegerField(null=True, blank=True, default=0)
    avatarUrl = models.CharField(max_length=255, null=True, blank=True, default='0')
    goodsId = models.IntegerField(null=True, blank=True, default=0)
    goodsName = models.CharField(max_length=255, null=True, blank=True, default='0')

    class Meta:
        verbose_name = '购买动态'
        verbose_name_plural = '购买动态'


class UserProfile(BaseModel):
    """用户详细"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatarUrl = models.CharField("头像", max_length=255, null=True, blank=True, default='0')
    birthdayProcessSuccessYear = models.IntegerField(null=True, blank=True, default=0)
    cardNumber = models.CharField(max_length=255, null=True, blank=True, default='0')
    city = models.CharField(max_length=255, null=True, blank=True, default='0')
    dateLogin = TimeStampField('登陆时间', null=True, blank=True, default=0)
    gender = models.IntegerField(null=True, blank=True, default=0)
    ipAdd = models.CharField(max_length=255, null=True, blank=True, default='0')
    ipLogin = models.CharField(max_length=255, null=True, blank=True, default='0')
    isFaceCheck = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    isIdcardCheck = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    isSeller = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    isTeamLeader = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    isTeamMember = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    levelRenew = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    mobileVisInvister = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=True)
    nick = models.CharField(max_length=255, null=True, blank=True, default='0')
    province = models.CharField(max_length=255, null=True, blank=True, default='0')
    referrerType = models.IntegerField(null=True, blank=True, default=0)
    source = models.IntegerField(null=True, blank=True, default=0)
    sourceStr = models.CharField(max_length=255, null=True, blank=True, default='0')
    status = models.IntegerField(null=True, blank=True, default=0)
    statusStr = models.CharField(max_length=255, null=True, blank=True, default='0')
    taskUserLevelSendMonth = models.IntegerField(null=True, blank=True, default=0)
    taskUserLevelSendPerMonth = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    taskUserLevelUpgrade = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'


class Order(BaseModel):
    """订单"""

    pay_number = models.CharField(max_length=255, null=True, blank=True, default='0')
    userId = models.CharField(max_length=255, null=True, blank=True, default='0')
    is_pay = models.IntegerField(null=True, blank=True, default=0)
    is_delivery = models.IntegerField(null=True, blank=True, default=0)
    is_close = models.IntegerField(null=True, blank=True, default=0)
    is_comment = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = '订单信息'
        verbose_name_plural = '订单信息'


class SessionInfo(BaseModel):
    """微信信息记录"""

    code = models.CharField(max_length=255, null=True, blank=True, default='0')
    openid = models.CharField(max_length=255, null=True, blank=True, default='0')
    session_key = models.CharField(max_length=255, null=True, blank=True, default='0')
    key = models.CharField(max_length=255, null=True, blank=True, default='0')

    class Meta:
        verbose_name = '微信授权记录'
        verbose_name_plural = '微信授权记录'


class ShopCart(BaseModel):
    """购物车"""

    name = models.CharField(max_length=255, null=True, blank=True, default='0')
    number = models.IntegerField('数量', null=True, blank=True, default='0')

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
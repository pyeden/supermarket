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
        return datetime.datetime.fromtimestamp(value)

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
        return f"{self._meta.app_label}_{self.id}"


class Goods(BaseModel):
    """商品"""

    afterSale = models.CharField(max_length=255, null=True, blank=True, default='0')
    categoryId = models.CharField(max_length=255, null=True, blank=True, default='0')
    characteristic = models.CharField(max_length=255, null=True, blank=True, default='0')
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
    minPrice = models.FloatField(null=True, blank=True, default=0)
    minScore = models.IntegerField(null=True, blank=True, default=0)
    name = models.CharField(max_length=255, null=True, blank=True, default='0')
    numberFav = models.IntegerField(null=True, blank=True, default=0)
    numberGoodReputation = models.IntegerField(null=True, blank=True, default=0)
    numberOrders = models.IntegerField(null=True, blank=True, default=0)
    numberReputation = models.IntegerField(null=True, blank=True, default=0)
    numberSells = models.IntegerField(null=True, blank=True, default=0)
    originalPrice = models.FloatField(null=True, blank=True, default=0)
    overseas = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    paixu = models.IntegerField(null=True, blank=True, default=0)
    pic = models.CharField(max_length=255, null=True, blank=True, default='0')
    pingtuan = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    pingtuanPrice = models.FloatField(null=True, blank=True, default=0)
    recommendStatus = models.IntegerField(null=True, blank=True, default=0)
    recommendStatusStr = models.CharField(max_length=255, null=True, blank=True, default='0')
    seckillBuyNumber = models.IntegerField(null=True, blank=True, default=0)
    sellEnd = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    sellStart = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=True)
    shopId = models.IntegerField(null=True, blank=True, default=0)
    status = models.IntegerField(null=True, blank=True, default=0)
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
        verbose_name = '商品'


class DiscountsCoupons(BaseModel):
    """折扣/优惠卷"""

    batchSendUid = models.IntegerField(null=True, blank=True, default=0)
    dateEndDays = models.IntegerField(null=True, blank=True, default=0)
    dateEndType = models.IntegerField(null=True, blank=True, default=0)
    dateStartType = models.IntegerField(null=True, blank=True, default=0)
    moneyHreshold = models.FloatField(null=True, blank=True, default=0)
    moneyMax = models.FloatField(null=True, blank=True, default=0)
    moneyMin = models.FloatField(null=True, blank=True, default=0)
    moneyType = models.IntegerField(null=True, blank=True, default=0)
    name = models.CharField(max_length=255, null=True, blank=True, default='0')
    needAmount = models.FloatField(null=True, blank=True, default=0)
    needScore = models.IntegerField(null=True, blank=True, default=0)
    needSignedContinuous = models.IntegerField(null=True, blank=True, default=0)
    numberGit = models.IntegerField(null=True, blank=True, default=0)
    numberGitNumber = models.IntegerField(null=True, blank=True, default=0)
    numberLeft = models.IntegerField(null=True, blank=True, default=0)
    numberPersonMax = models.IntegerField(null=True, blank=True, default=0)
    numberTotle = models.IntegerField(null=True, blank=True, default=0)
    numberUsed = models.IntegerField(null=True, blank=True, default=0)
    sendBirthday = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    sendInviteM = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    sendInviteS = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    sendRegister = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    showInFront = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=True)
    status = models.IntegerField(null=True, blank=True, default=0)
    statusStr = models.CharField(max_length=255, null=True, blank=True, default='0')
    type = models.CharField(max_length=255, null=True, blank=True, default='0')

    class Meta:
        verbose_name = '折扣优惠'


class Config(BaseModel):
    """配置信息"""

    key = models.CharField("配置", max_length=255, null=True, blank=True, default='0')
    remark = models.CharField("备注", max_length=255, null=True, blank=True, default='0')
    value = models.CharField("参数", max_length=255, null=True, blank=True, default='0')

    class Meta:
        verbose_name = '配置'


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


class GoodsCategory(BaseModel):
    """商品分类"""

    icon = models.CharField("图标", max_length=255, null=True, blank=True, default='0')
    key = models.CharField(max_length=255, null=True, blank=True, default='0')
    name = models.CharField(max_length=255, null=True, blank=True, default='0')
    type = models.CharField(max_length=255, null=True, blank=True, default='0')
    level = models.IntegerField(null=True, blank=True, default=0)
    paixu = models.IntegerField(null=True, blank=True, default=0)
    pid = models.IntegerField(null=True, blank=True, default=0)
    shopId = models.IntegerField(null=True, blank=True, default=0)
    userId = models.IntegerField(null=True, blank=True, default=0)
    isUse = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=True)

    class Meta:
        verbose_name = '商品分类'


class Notice(BaseModel):

    isShow = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=True)
    title = models.CharField(max_length=255, null=True, blank=True, default='0')
    userId = models.IntegerField(null=True, blank=True, default=0)


class LiveRooms(BaseModel):

    close_comment = models.IntegerField(null=True, blank=True, default=0)
    close_kf = models.IntegerField(null=True, blank=True, default=0)
    is_feeds_public = models.IntegerField(null=True, blank=True, default=0)
    anchor_name = models.CharField(max_length=255, null=True, blank=True, default='0')
    close_like = models.IntegerField(null=True, blank=True, default=0)
    live_type = models.IntegerField(null=True, blank=True, default=0)
    roomid = models.IntegerField(null=True, blank=True, default=0)
    feeds_img = models.CharField(max_length=255, null=True, blank=True, default='0')
    creater_openid = models.CharField(max_length=255, null=True, blank=True, default='0')
    name = models.CharField(max_length=255, null=True, blank=True, default='0')
    close_replay = models.IntegerField(null=True, blank=True, default=0)
    share_img = models.CharField(max_length=255, null=True, blank=True, default='0')
    cover_img = models.CharField(max_length=255, null=True, blank=True, default='0')
    close_goods = models.IntegerField(null=True, blank=True, default=0)
    live_status = models.IntegerField(null=True, blank=True, default=0)


class HomeAdvertising(BaseModel):
    """首页弹出广告"""

    name = models.CharField(max_length=255, null=True, blank=True, default='0')
    type = models.CharField(max_length=255, null=True, blank=True, default='0')
    val = models.CharField(max_length=255, null=True, blank=True, default='0')

    class Meta:
        verbose_name = '首页弹出广告'


class SiteGoodsDynamic(BaseModel):
    """网站商品动态"""

    nick = models.CharField(max_length=255, null=True, blank=True, default='0')
    uid = models.IntegerField(null=True, blank=True, default=0)
    number = models.IntegerField(null=True, blank=True, default=0)
    orderId = models.IntegerField(null=True, blank=True, default=0)
    avatarUrl = models.CharField(max_length=255, null=True, blank=True, default='0')
    goodsId = models.IntegerField(null=True, blank=True, default=0)
    goodsName = models.CharField(max_length=255, null=True, blank=True, default='0')

    class Meta:
        verbose_name = '网站商品动态'


class KanJiaSet(BaseModel):

    goodsId = models.IntegerField(null=True, blank=True, default=0)
    helpPriceMax = models.FloatField(null=True, blank=True, default=0)
    helpPriceMin = models.FloatField(null=True, blank=True, default=0)
    helpTimes = models.IntegerField(null=True, blank=True, default=0)
    minPrice = models.FloatField(null=True, blank=True, default=0)
    number = models.IntegerField(null=True, blank=True, default=0)
    numberBuy = models.IntegerField(null=True, blank=True, default=0)
    originalPrice = models.FloatField(null=True, blank=True, default=0)
    reduction = models.BooleanField(null=True, blank=True, choices=BOOL_CHOICE, default=False)
    status = models.IntegerField(null=True, blank=True, default=0)
    statusStr = models.CharField(max_length=255, null=True, blank=True, default='0')


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
        verbose_name = '用户详细信息'


class MoneyInfo(BaseModel):
    """钱包信息"""

    balance = models.IntegerField(null=True, blank=True, default=0)
    freeze = models.IntegerField(null=True, blank=True, default=0)
    fxCommisionPaying = models.IntegerField(null=True, blank=True, default=0)
    growth = models.IntegerField(null=True, blank=True, default=0)
    score = models.IntegerField(null=True, blank=True, default=0)
    scoreLastRound = models.IntegerField(null=True, blank=True, default=0)
    totalPayAmount = models.IntegerField(null=True, blank=True, default=0)
    totalPayNumber = models.IntegerField(null=True, blank=True, default=0)
    totalScore = models.IntegerField(null=True, blank=True, default=0)
    totalWithdraw = models.IntegerField(null=True, blank=True, default=0)
    totleConsumed = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = '钱包'


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

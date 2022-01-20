from django.apps import AppConfig


VERBOSE_APP_NAME = '商品管理'


class ShopConfig(AppConfig):
    name = 'app'
    verbose_name = VERBOSE_APP_NAME
    main_menu_index = 3

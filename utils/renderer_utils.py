from rest_framework.renderers import JSONRenderer


# 导入控制返回的JSON格式的类
class CustomRenderer(JSONRenderer):
    # 重构render方法
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            # 判断实例的类型，返回的数据可能是列表也可能是字典
            if isinstance(data, dict):
                # 如果是字典的话应该是返回的数据，会包含msg,code,status等字段必须抽离出来
                msg = data.pop('msg', 'success')
                code = data.pop('code', 0)
                data = data.pop('data', 0)
            # 自定义返回数据格式
            ret = {
                'msg': msg,
                'code': code,
                'data': data.get('results',[]),
                "count": 50,
                "next": "http://127.0.0.1:8088/api/v1/tests/?page=2",
                "previous": None,
            }
            # 返回JSON数据
            return super().render(ret, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)

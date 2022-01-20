from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, _positive_int

from utils.response_utils import BaseResponse


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page'
    max_page_size = 10000


class ShortResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page'
    max_page_size = 100


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page'
    max_page_size = 1000


class CustomLimitOffsetPagination(LimitOffsetPagination):
    limit = None

    def get_limit(self, request):
        if self.limit_query_param:
            try:
                value = request.query_params[self.limit_query_param]
                if int(value) == -1:
                    return int(value)
                else:
                    return _positive_int(
                        value,
                        strict=True,
                        cutoff=self.max_limit
                    )
            except (KeyError, ValueError):
                pass
        return self.default_limit

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit == -1:
            return list(queryset)
        return super().paginate_queryset(queryset, request, view=None)

    def get_paginated_response(self, data):

        return BaseResponse(data={'count': self.count, 'results': data})


class NoticeListPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'pageSize'
    max_page_size = 100

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    self.get_query_params(request)[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_page_number(self, request, paginator):
        page_number = self.get_query_params(request).get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        return page_number

    @staticmethod
    def get_query_params(request):
        return request.data if request._request.method == 'POST' else request.query_params.dict()
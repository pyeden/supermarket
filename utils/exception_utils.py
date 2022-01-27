from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from django.utils.translation import gettext_lazy as _

from utils.code_utils import CODE_NOT_FOUND_ERROR, MSG_NOT_FOUND_ERROR, MSG_UNKNOWN_ERROR, CODE_UNKNOWN_ERROR, \
    CODE_AUTH_ERROR, MSG_AUTH_ERROR, CODE_SERVER_ERROR, MSG_SERVER_ERROR, MSG_REJECT_ERROR, CODE_REJECT_ERROR, \
    CODE_METHOD_ERROR, MSG_METHOD_ERROR, MSG_PARAMETER_ERROR, CODE_PARAMETER_ERROR


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data.clear()
        response.data['data'] = []

        if response.status_code == 404:
            try:
                response.data['message'] = MSG_NOT_FOUND_ERROR
                response.data['code'] = CODE_NOT_FOUND_ERROR
            except KeyError:
                response.data['message'] = MSG_NOT_FOUND_ERROR

        if response.status_code == 400:
            response.data['message'] = MSG_PARAMETER_ERROR
            response.data['code'] = CODE_PARAMETER_ERROR

        elif response.status_code == 401:
            response.data['message'] = exc.detail
            response.data['code'] = CODE_AUTH_ERROR

        elif response.status_code >= 500:
            response.data['message'] = MSG_SERVER_ERROR
            response.data['code'] = CODE_SERVER_ERROR

        elif response.status_code == 403:
            response.data['message'] = MSG_REJECT_ERROR
            response.data['code'] = CODE_REJECT_ERROR

        elif response.status_code == 405:
            response.data['message'] = MSG_METHOD_ERROR
            response.data['code'] = CODE_METHOD_ERROR
    return response


class WXFailed(APIException):
    """
    微信相关错误
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('Incorrect authentication credentials.')
    default_code = 50001


class DbFailed(APIException):
    """
    数据库操作相关错误
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('操作数据库错误.')
    default_code = 50002

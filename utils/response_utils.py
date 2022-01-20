from rest_framework.response import Response
from utils.code_utils import CODE_SUCCESS, MSG_SUCCESS
from rest_framework import status


class BaseResponse(Response):
    def __init__(
            self,
            code=CODE_SUCCESS,
            message=MSG_SUCCESS,
            data=None,
            headers=None,
            status_code=status.HTTP_200_OK,
            template_name=None,
            exception=False,
            content_type='application/json',

    ):
        super().__init__(None, status=status_code)
        self.data = {"code": code, "msg": message, "data": data if data is not None else {}}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in headers.items():
                self[name] = value



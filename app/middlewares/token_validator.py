import time
import typing
import re

import jwt

from fastapi.params import Header
from jwt.exceptions import ExpiredSignatureError,DecodeError
from pydantic import BaseModel
from starlette.requests import Request
from starlette.datastructures import URL, Headers
from starlette.responses import JSONResponse,Response
from app.common.consts import EXCEPT_PATH_LIST,EXCEPT_PATH_REGEX
from app.errors import exceptions as ex
from starlette.responses import PlainTextResponse, RedirectResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from app.common import config, consts
from app.common.config import conf
from app.errors.exceptions import APIException
from app.models import UserToken

from app.util.date_utils import D
from app.util.logger import api_logger


async def access_control(request: Request, call_next):
    request.state.start = time.time()
    request.state.inspect = None
    request.state.user = None
    request.state.is_admin_access = None
    ip = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else request.client.host
    request.state.ip= ip.split(",")[0] if "," in ip else ip
    headers = request.headers
    cookies = request.cookies
    url = request.url.path
    if await url_pattern_check(url,EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
        response = await call_next(request)
        if url != "/":
            await api_logger(request=request)
        return response

    try:
        if request.url.path.startswith("/api"):
            # api 인경우 헤더로 토큰 검사
            if "authorization" in request.headers.keys():
                token_info = await token_decode(access_token=request.headers.get("Authorization"))
                request.state.user = UserToken(**token_info)

            # 토큰 없음
            else:
                if "Authorization" not in request.headers.keys():
                    raise ex.NotAuthorized()
        else:
            # 템플릿 렌더링인 경우 쿠키에서 토큰 검사
            print(cookies)
            cookies["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJJRCI6MTUsImVtYWlsIjoic3RyaW5nMTNAc3RyaW5nLmNvbSIsInBob25lIjpudWxsLCJwcm9maWxlX2ltZyI6bnVsbCwic25zX3R5cGUiOm51bGx9.AQbpZ_wuj_H4xFYtX9GFIENWvnpGDyOKJW70f4fttbs"

            if "Authorization" not in request.cookies.keys():
                raise ex.NotAuthorized()

            token_info = await token_decode(access_token=request.cookies.get("Authorization"))
            request.state.user = UserToken(**token_info)

        response = await call_next(request) #함수 실행 api
        await api_logger(request=request,response=response)
    except Exception as e:
        error = await exception_handler(e)
        error_dict = dict(status=error.status_code,msg=error.msg,detail=error.detail,code=error.code)
        response = JSONResponse(status_code=error.status_code,content=error_dict)
        await api_logger(request=request,response=response)
    return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False

async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(access_token, key=consts.JWT_SECRET, algorithms=[consts.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise ex.TokenExpiredEx()
    except DecodeError:
        raise ex.TokenDecodeEx()
    return payload

async def exception_handler(error: Exception):
    if not isinstance(error,APIException):
        error = APIException(ex=error,detail=str(error))
    return error
from dataclasses import asdict
from typing import Optional

import uvicorn
from fastapi import FastAPI,Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.common.consts import EXCEPT_PATH_LIST,EXCEPT_PATH_REGEX
from app.database.conn import db
from app.common.config import conf
from app.middlewares.token_validator import access_control
from app.middlewares.trusted_hosts import TrustedHostMiddleware
from app.routes import index, auth , users

from app.common.consts import DEV_URL,DEV_PORT


API_KEY_HEADER = APIKeyHeader(name="Authorization",auto_error=False)
def create_app():
    """
    앱 함수 실행
    :return:
    """
    c = conf()
    app = FastAPI()
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)
    # 데이터 베이스 이니셜라이즈

    # 레디스 이니셜라이즈

    # 미들웨어 정의
    #=> 스택 구조여서 실제 실행은 맨 아래 메서드부터 실행, accesscontrol 이 아래 있으면 오류가 발생함. cors 미들웨어가 선행 실행되어야 오류가 발생하지 않음
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=conf().TRUSTED_HOSTS,except_path=["/health"])

    # 라우터 정의
    app.include_router(index.router)
    app.include_router(auth.router,tags=["Authentication"],prefix="/api")
    app.include_router(users.router,tags =["Users"],prefix="/api",dependencies=[Depends(API_KEY_HEADER)])

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host=DEV_URL, port=DEV_PORT, reload=True)
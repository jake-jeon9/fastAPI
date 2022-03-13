from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.database.conn import db
from app.database.schema import Users
from app.models import Token,SnsType
from app import models

router  = APIRouter()

@router.get("/")
async def index():
    """
    :param session:
    :return:
    """

    current_time = datetime.utcnow();
    return Response(f"Notification API (UTC : {current_time.strftime('%Y.%m.%d %H:%M:%S ')}")


@router("/register/{sns_type}",status_code = 200,responses_model =Token)
async def register(sns_type :SnsType, reg_info : models.UserRegister, session:Session =
Depends((db.session)) :
    """
    회원 가입 APU
    :param sns_type:
    :param reg_info:
    :param session:
    :return:
    """
    if sns_type == SnsType.email :
        is_exist = await is_email_exist(reg_info.email)
        if not reg_info.email or reg_info.pw:
            return JSONResponse(status_code = 400,content= dict(msg = "Email and Pw must be provided"))

        if is_exist :
            return JSONResponse(status_code = 400, content = dict(msg="Email_exists"))

        hash_pw = bc

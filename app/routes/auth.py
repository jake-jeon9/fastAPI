
from datetime import datetime,timedelta

import bcrypt
import jwt
from fastapi import APIRouter,Depends

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db
from app.database.schema import Users
from app.models import SnsType, Token, UserToken, UserRegister

"""
 1. 구글 로그인을 위한 구글 앱 준비 (구글 개발자 도구)
 2. FB 로그인을 위한 FB 앱 준비 (FB 개발자 도구)
 3. 카카오 로그인을 위한 카카오 앱준비( 카카오 개발자 도구)
 4. 이메일, 비밀번호로 가입 (v)
 5. 가입된 이메일, 비밀번호로 로그인, (v)
 6. JWT 발급 (v)
 7. 이메일 인증 실패시 이메일 변경
 8. 이메일 인증 메일 발송
 9. 각 SNS 에서 Unlink 
 10. 회원 탈퇴
 11. 탈퇴 회원 정보 저장 기간 동안 보유(법적 최대 한도차 내에서, 가입 때 약관 동의 받아야 함, 재가입 방지 용도로 사용하면 가능)
 """

router = APIRouter()

@router.post("/register/{sns_type}",status_code=200,response_model=Token)
async def register(sns_type : SnsType,reg_info : UserRegister,session : Session = Depends(db.session)):
    """
    회원가입 API
    :param sns_type:
    :param reg_info:
    :param session:
    :return:
    """
    if sns_type == SnsType.email :
        is_exist = is_email_exist(reg_info.email)
        print("is_exist : "+str(is_exist))
        print("email : "+reg_info.email)
        print("pw : "+reg_info.pw)

        # 입력값 검사
        if not reg_info.email or not reg_info.pw :
            return JSONResponse(status_code=400,content=dict(msg="Email and pw must be provided"))

        #유효성 검사
        if is_exist :
            return JSONResponse(status_code=400,content=dict(msg="EMAIL_EXIASTS"))

        cnt = getCount()
        strCnt = str(cnt)
        strCnt = strCnt.replace("(","")
        strCnt = strCnt.replace(",","")
        strCnt = strCnt.replace(")","")
        print(strCnt)
        intCnt = int(strCnt)+1
        #pw 헤시
        hash_pw = bcrypt.hashpw(reg_info.pw.encode("utf-8"),bcrypt.gensalt())

        #생성
        new_user = Users.create(session,auto_commit=True,pw=hash_pw,email=reg_info.email,ID=intCnt)

        #토큰
        token = dict(Authorization = f"Bearer{create_access_token(date=UserToken.from_orm(new_user).dict(exclude={'pw'}),)}")
        print("token :" +token)
        return token
    return JSONResponse(status_code=400,content=dict(mst="NOT_SUPPORTED"))


@router.post("/login/{sns_type}",status_code=200)
async def login(sns_type: SnsType,user_info : UserRegister):
    if sns_type == SnsType.email :
        is_exist = await is_email_exist(user_info.email)
        if not user_info.email or not user_info.pw :
            return JSONResponse(status_code=400, content=dict(msg="Email and pw must be provided"))
        if not is_exist:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
        user = Users.get(email=user_info.email)
        is_verified = bcrypt.checkpw(user_info.pw.encode("utf-8"),user.pw.encode("utf-8"))
        if not is_verified :
            return JSONResponse(status_code=400,content=dict(msg = "NO_MATCH_USER"))
        token = dict(
            Authorization=f"Bearer{create_access_token(date=UserToken.from_orm(user).dict(exclude={'pw'}), )}")
        return token
    return JSONResponse(status_code=400, content=dict(mst="NOT_SUPPORTED"))

def is_email_exist(email : str):
    get_email = Users.get(email = email)
    if get_email :
        return True
    return False

def create_access_token(*,data:dict=None,expires_delta:int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp":datetime.utcnow() + timedelta(hours=expires_delta)})
        encoded_jwt = jwt.encode(to_encode,JWT_SECRET,algorithm = JWT_ALGORITHM)
        return encoded_jwt

def getCount() :
    count = Users.getCount()
    print(str(count)+"<< ")
    return count
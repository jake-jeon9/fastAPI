from datetime import datetime
from enum import Enum
from typing import List,Optional

from pydantic import Field
from pydantic.main import BaseModel
from pydantic import EmailStr, IPvAnyAddress

# pydamtic 은 객체화 해서 사용 json 형태로 사용, docs

class UserRegister(BaseModel):
    # pip install 'pydantic[email]'
    email : EmailStr = None
    pw : str = None

class SnsType (str,Enum): #Enum 은 1개만 선택
    email : str = "email"
    facebook : str = "facebook"
    google : str = "google"
    kakao : str ="kakao"
    naver : str = "naver"
    defalut : "None"

class Token(BaseModel) :
    Authorization : str =None

class UserToken(BaseModel) :
    ID : int
    pw : str =None
    email : str = None
    phone : str = None
    profile_img : str = None
    sns_type : str = None

    class Config :
        orm_mode = True
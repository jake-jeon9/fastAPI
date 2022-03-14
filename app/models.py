from datetime import datetime
from enum import Enum
from typing import List,Optional

from pydantic import Field
from pydantic.main import BaseModel
from pydantic import EmailStr, IPvAnyAddress



class UserRegister(BaseModel):
    # pip install 'pydantic[email]'
    email : str= None
    pw : str = None

class SnsType (str,Enum):
    email : str = "email"
    facebook : str = "facebook"
    google : str = "google"
    kakao : str ="kakao"
    naver : str = "naver"


class Token(BaseModel) :
    Authorization : str =None

class UserToken(BaseModel) :
    id : int
    pw : str =None
    email : str = None
    phone : str = None
    profile_img : str = None
    sns_type : str = None

    class Config :
        orm_mode = True
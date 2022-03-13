from enum import Enum

from pydantic.main import BaseModel
from pydantic.networks import EmailStr


class UserRegister(BaseModel):
    email : EmailStr = None
    pw:str = None

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
from dataclasses import dataclass, asdict
from os import path, environ

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Config:
    """
    기본 Configuration
    """
    BASE_DIR : str = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True # echp 설정을 통해 디버깅
    DEBUG : bool = False
    TEST_MODE : bool = False
    MYSQL_USER = 'root'
    MYSQL_PW = '1234'
    MYSQL_HOST = 'localhost'
    MYSQL_DB = 'docker'
    DB_URL : str = environ.get("DB_URL","mysql+pymysql://{user}:{pw}@{host}:3306/{db}".format(
        user=MYSQL_USER,pw=MYSQL_PW,host=MYSQL_HOST,db=MYSQL_DB))


@dataclass
class LocalConfig(Config):
    #TRUSTED_HOSTS = ["*"]
    #ALLOW_SITE = ["*"]
    #DEBUG: bool = True
    PROJ_RELOAD : bool = True
    DB_URL: str = "mysql+pymysql://fastapi:user1234@localhost:3306/docker?charset=utf8mb4"
    #DB_URL: str = "mysql+pymysql://root:1234@localhost:3306/docker?charset=utf8mb4"

@dataclass
class ProdConfig(Config):
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]

@dataclass
class TestConfig(Config):
    DB_URL: str = "mysql+pymysql://fastapi@localhost/pythonProject?charset=utf8mb4"
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    TEST_MODE: bool = True


def conf():
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig(), local=LocalConfig())
    return config.get(environ.get("API_ENV", "local"))
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Enum,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import Session, relationship
from app.database.conn import Base, db
from sqlalchemy import text,inspect

class BaseMixin:
    #ID = Column(Integer,primary_key = True,index = True)
    ins_date = Column(DateTime, nullable = False, default = func.utc_timestamp())
    upt_date = Column(DateTime, nullable = False, default = func.utc_timestamp(),onupdate=func.utc_timestamp())

    def __init__(self):
        self._q = None
        self._session = None
        self.served = None

    def all_columns(self):
        return inspect(self.__table__)

    def __hash__(self):
        return hash(self.id)


    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls,session : Session, auto_commit=False,**kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit:
        :param kwargs:
        :return:
        """

        obj = cls()
        table = obj.all_columns()
        for col in  table.c :
            col_name = col.name
            if col_name in kwargs:
                print("colname : "+col_name)
                # 테이벌.컬럼 = value
                setattr(obj,col_name,kwargs.get(col_name))

        session.add(obj)
        session.flush()
        if auto_commit :
            session.commit()
        return obj

    @classmethod
    def get(cls,session : Session = None, **kwargs):
        """
        Simply get a Row
        :param kwargs:
        :return:
        """
        session = next(db.session()) if not session else session
        query = session.query(cls)
        for key, val in kwargs.items():
            col = getattr(cls,key)
            query = query.filter(col == val)

        if query.count() > 1:
            raise Exception("Only one row is supposed to be returned, but got more than one.")
        result = query.first()
        if not session:
            session.close()
        return result

    @classmethod
    def getCount(cls,session :Session = None, **kwargs):
        session = next(db.session()) if not session else session
        count = session.execute(text("select count(1) from docker.`user`"))
        return count.first()

    @classmethod
    def filter(cls, session: Session = None, **kwargs):
        """
        Simply get a Row
        :param session:
        :param kwargs:
        :return:
        """
        cond = []
        for key, val in kwargs.items():
            key = key.split("__")
            if len(key) > 2:
                raise Exception("No 2 more dunders")
            col = getattr(cls, key[0])
            if len(key) == 1: cond.append((col == val))
            elif len(key) == 2 and key[1] == 'gt': cond.append((col > val))
            elif len(key) == 2 and key[1] == 'gte': cond.append((col >= val))
            elif len(key) == 2 and key[1] == 'lt': cond.append((col < val))
            elif len(key) == 2 and key[1] == 'lte': cond.append((col <= val))
            elif len(key) == 2 and key[1] == 'in': cond.append((col.in_(val)))
        obj = cls()
        if session:
            obj._session = session
            obj.served = True
        else:
            obj._session = next(db.session())
            obj.served = False
        query = obj._session.query(cls)
        query = query.filter(*cond)
        obj._q = query
        return obj


class Users(Base,BaseMixin):
    print("테이블 진입")
    __tablename__ = "user"
    ID = Column(String(length=255),primary_key=True)
    status = Column(Enum("active", "deleted", "blocked"), default="active")
    email = Column(String(length=30), nullable=True)
    pw = Column(String(length=200), nullable=True)
    name = Column(String(length=20), nullable=True)
    phone = Column(String(length=10), nullable=True, unique=True)
    profile_img = Column(String(length=200), nullable=True)
    sns_type = Column(Enum("facebook", "google", "kakao","email","None"),nullable=True)
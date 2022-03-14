from sqlalchemy.orm import Session
from app.database.conn import Base
from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declarative_base
from app.database.conn import Base,db
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Enum,
    Boolean
    )

class BaseMixin:
    id = Column(Integer,primary_key = True,index = True)
    created_at = Column(DateTime, nullable = False, default = func.utc_timestamp())
    updated_at = Column(DateTime, nullable = False, default = func.utc_timestamp(),onupdate=func.utc_timestamp())

    def all_columns(self):
        return [c for c in self.__table__columns if c.primary_key is False and c.name != "created_at"]


    def __hash__(self):
        return hash(self.id)

    def create(cls,session : Session, auto_commit=False,**kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit:
        :param kwargs:
        :return:
        """
        obj = cls()
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj,col_name,kwargs.get(col_name))
        session.add(obj)
        session.flush()
        if auto_commit :
            session.commit()
        return obj

    @classmethod
    def get(cls,**kwargs):
        """
        Simply get a Row
        :param kwargs:
        :return:
        """
        session = next(db.session())
        query = session.query(cls)
        for key, val in kwargs.items():
            col = getattr(cls,key)
            query = query.fillter(col == val)


class Users(Base,BaseMixin):
    __tablename__ = "docker.user"
    status = Column(Enum("active", "deleted", "blocked"), default="active")
    email = Column(String(length=255), nullable=True)
    pw = Column(String(length=2000), nullable=True)
    name = Column(String(length=255), nullable=True)
    phone_number = Column(String(length=20), nullable=True, unique=True)
    profile_img = Column(String(length=1000), nullable=True)
    sns_type = Column(Enum("FB", "G", "K"), nullable=True)
    marketing_agree = Column(Boolean, nullable=True, default=True)
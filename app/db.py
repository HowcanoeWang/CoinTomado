# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Text, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///data.db', echo=True)
DBSession = sessionmaker(bind=engine)

Base = declarative_base()

###############
#    Models   #
###############

#===== CoinBlock =====
class Record(Base):
    __tablename__ = 'record'

    id = Column(Integer, primary_key=True)
    date = Column(Integer, index=True, default=datetime.now().strftime("%Y%m%d"))
    time_block = Column(Integer, index=True)
    action_id = Column(Integer, ForeignKey('action.id'))
    remark_id = Column(Integer, ForeignKey('remark.id'))
    kind_id = Column(Integer, ForeignKey('kind.id'))
    rowspan = Column(Integer, default=1)


class Action(Base):
    __tablename__ = 'action'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
 
 
class Remark(Base):
    __tablename__ = 'remark'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
 
 
class Kind(Base):
    __tablename__ = 'kind'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    color = Column(String(32))
 
 
class Summary(Base):
    __tablename__ = 'summary'
    
    id = Column(Integer, primary_key=True)
    date = Column(Integer, index=True, default=datetime.now().strftime("%Y%m%d"))
    type = Column(Integer, default=0)
    contents = Column(String(1024), default='# 每日总结\n')
    
#===== Todo ======


#===== Pomodoro =====
    
##############
#  Controls  # 
##############  
    
def update():
    # 创建session对象:
    session = DBSession()
    # 创建新User对象:
    new_user = Record(id='0')
    # 添加到session:
    session.add(new_user)
    # 提交即保存到数据库:
    session.commit()
    # 关闭session:
    session.close()

Base.metadata.create_all(engine)
update()
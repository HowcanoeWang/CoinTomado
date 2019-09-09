# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///data.db', echo=True)
DBSession = sessionmaker(bind=engine)

Base = declarative_base()

###############
#    Models   #
###############

# ===== CoinBlock =====
class Coin(Base):
    __tablename__ = 'coin'

    id = Column(Integer, primary_key=True)
    date = Column(Integer, index=True, default=datetime.now().strftime("%Y%m%d"))
    time_block = Column(Integer, index=True)
    behavior_id = Column(Integer, ForeignKey('behavior.id'))
    remark_id = Column(Integer, ForeignKey('remark.id'))
    kind_id = Column(Integer, ForeignKey('kind.id'))
    rowspan = Column(Integer, default=1)


class Behavior(Base):
    __tablename__ = 'behavior'
    
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
    color = Column(Integer, ForeignKey('color.id'))


class Color(Base):
    __tablename__ = 'color'

    id = Column(Integer, primary_key=True)
    name = Column(String(8), unique=True)
    red = Column(Integer)
    green = Column(Integer)
    blue = Column(Integer)
    alpha = Column(Integer)
 

class Summary(Base):
    __tablename__ = 'summary'
    
    id = Column(Integer, primary_key=True)
    date = Column(Integer, index=True, default=datetime.now().strftime("%Y%m%d"))
    type = Column(Integer, default=0)
    contents = Column(String(1024), default='# 每日总结\n')

# ===== CurrentScreen =====
class ScreenRecord(Base):
    __tablename__ = 'screen_record'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, index=True, default=datetime.now())
    device_id = Column(Integer, ForeignKey('device.id'))
    app_id = Column(Integer, ForeignKey('app.id'))
    app_title_id = Column(Integer, ForeignKey('app_title.id'))


class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)


class App(Base):
    __tablename__ = 'app'

    id = Column(Integer, primary_key=True)
    name = Column(Integer, unique=True)
    work_white_list = Column(Boolean, default=True)

class AppTitle(Base):
    __tablename__ = 'app_title'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)

# ===== TodoFunction ======
class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    kind_id = Column(Integer, ForeignKey('kind.id'))
    task_id = Column(Integer, ForeignKey('task.id'))
    comments = Column(String(128), default='')

class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    subtask_id = Column(Integer, ForeignKey('subtask.id'))
    status = Column(Boolean, default=True)
    urgent = Column(Integer, default=0)
    deadline = Column(Integer, default=datetime.now().strftime("%Y%m%d"))
    pred_num = Column(Integer, default=1)
    comments = Column(String(128), default='')


class Subtask(Base):
    __tablename__ = 'subtask'

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    status = Column(Boolean, default=True)

# ===== Pomodoro =====
class Tomatodo(Base):
    __tablename__ = 'tomatodo'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))
    subtask_id = Column(Integer, ForeignKey('subtask.id'))
    st_time = Column(DateTime, default=datetime.now())
    ed_time = Column(DateTime, default=datetime.now())
    interrupted = Column(Boolean, default=False)
    reason = Column(String(128), default='')

##############
#  Controls  # 
##############  
    
def update():
    # 创建session对象:
    session = DBSession()
    # 创建新User对象:
    new_user = Coin(id='0')
    # 添加到session:
    session.add(new_user)
    # 提交即保存到数据库:
    session.commit()
    # 关闭session:
    session.close()

Base.metadata.create_all(engine)
update()
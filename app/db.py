# -*- coding: utf-8 -*-
import struct
from datetime import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

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
    hex = Column(String(6), unique=True)
    alpha = Column(Integer)
    name = Column(String(8), unique=True)
 

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


class DB_Operator(object):

    def __init__(self, db_file):
        self.engine = create_engine(f'sqlite:///{db_file}', echo=True)
        self.sessionmaker = sessionmaker(bind=self.engine)

    def create_db(self):
        Base.metadata.create_all(self.engine)

        self.add_color(color=(210, 223, 224), name='淡灰')
        self.add_color(color=(32, 78, 135), name='靛青')
        self.add_color(color=(60, 198, 237), name='天蓝')
        self.add_color(color=(255, 176, 63), name='橙黄')
        self.add_color(color=(132, 45, 115), name='深紫')
        self.add_color(color=(238, 49, 107), name='品红')
        self.add_color(color=(255, 212, 38), name='金黄')
        self.add_color(color=(), name='草绿')
        self.add_color(color=(), name='肉红')
        self.add_color(color=(), name='淡紫')
        self.add_color(color=(), name='浅绿')
        self.add_color(color=(), name='水绿')
        self.add_color(color=(), name='中紫')
        self.add_color(color=(), name='海蓝')
        self.add_color(color=(), name='洋红')
        self.add_color(color=(), name='淡红')
        self.add_color(color=(), name='银灰')
        self.add_color(color=(), name='棕褐')
        self.add_color(color=(), name='毯绿')
        self.add_color(color=(), name='纯黑')



    def add_coin(self, date, time_block, behavior, remark, kind, rowspan=1):
        session = self.sessionmaker()

        behavior_id = self.add_behavior(behavior)
        remark_id = self.add_remark(remark)
        #new_coin = Coin(date=date, time_block=time_block, rowspan=rowspan)

        #session.add(new_coin)
        #session.commit()
        #session.close()

    def add_behavior(self, name):
        session = self.sessionmaker()
        id_query = session.query(Behavior).filter_by(name=name).first()
        if id_query is not None:
            # this exists in table
            behavior_id = id_query.id
        else:
            # not exist
            new_behavior = Behavior(name=name)
            session.add(new_behavior)
            session.commit()
            id_query = session.query(Behavior).filter_by(name=name).first()
            behavior_id = id_query.id

        session.close()
        return behavior_id

    def edit_behavior(self, behavior_id, name_new=None):
        pass

    def add_remark(self, name):
        session = self.sessionmaker()
        id_query = session.query(Remark).filter_by(name=name).first()
        if id_query is not None:
            # this exists in table
            remark_id = id_query.id
        else:
            # not exist
            new_remark = Remark(name=name)
            session.add(new_remark)
            session.commit()
            id_query = session.query(Remark).filter_by(name=name).first()
            remark_id = id_query.id

        session.close()
        return remark_id

    def edit_remark(self, remark_id, name_new=None):
        pass

    def add_kind(self, name, color_rgba=None, color_name=None):
        pass

    def edit_kind(self, kind_id, name_new=None, color_new=None):
        pass

    def add_color(self, color=None, alpha=255, name=''):
        # color is string = hex code
        # color is tuple = (r, g, b) code
        # alpha
        session = self.sessionmaker()
        if isinstance(color, tuple):
            hex = self.rgb2hex(color)
        else:
            hex = color

        new_color = Color(hex=hex, alpha=alpha, name=name)
        session.add(new_color)
        session.commit()
        session.close()


    def edit_color(self, color_id, name_new=None, rgba_new=None):
        pass

    def add_summary(self, date, sum_type, contents):
        pass

    def edit_summary(self, sum_id, date_new=None, sum_type_new=None, contents_new=None):
        pass

    @staticmethod
    def rgb2hex(rgb):
        return '#%02x%02x%02x' % rgb


if __name__ == '__main__':
    db_name = 'data_test.db'
    import os
    db = DB_Operator(db_name)
    if not os.path.exists(db_name):
        db.create_db()
    db.add_coin(date=20190817, time_block=1, behavior='rua', remark=1, kind=1)
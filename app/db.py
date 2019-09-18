# -*- coding: utf-8 -*-
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
    color_id = Column(Integer, ForeignKey('color.id'))


class Color(Base):
    __tablename__ = 'color'

    id = Column(Integer, primary_key=True)
    hex = Column(String(6), unique=True)
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


class DBOperator(object):

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
        self.add_color(color=(147, 208, 79), name='草绿')
        self.add_color(color=(243, 111, 142), name='肉红')
        self.add_color(color=(147, 114, 185), name='淡紫')
        self.add_color(color='#85ffda', name='浅绿')
        self.add_color(color='#5ce5aa', name='水绿')
        self.add_color(color='#8924e7', name='中紫')
        self.add_color(color='#3673ff', name='海蓝')
        self.add_color(color='#fd51d9', name='洋红')
        self.add_color(color='#ff6060', name='淡红')
        self.add_color(color='#b6b4b7', name='银灰')
        self.add_color(color='#bd998d', name='棕褐')
        self.add_color(color='#00bfa5', name='毯绿')
        self.add_color(color='#3b3b3b', name='纯黑')

        self.add_kind(name='尽情娱乐', color_id=self.get_color_id('天蓝'))
        self.add_kind(name='休息放松', color_id=self.get_color_id('草绿'))
        self.add_kind(name='高效工作', color_id=self.get_color_id('金黄'))
        self.add_kind(name='强迫工作', color_id=self.get_color_id('橙黄'))
        self.add_kind(name='无效拖延', color_id=self.get_color_id('中紫'))
        self.add_kind(name='小憩睡眠', color_id=self.get_color_id('淡灰'))

    def add_coin(self, date, time_block, behavior, remark, kind, rowspan=1):
        session = self.sessionmaker()

        behavior_id = self.add_behavior(behavior)
        remark_id = self.add_remark(remark)
        if isinstance(kind, str):
            kind_id = self.add_kind(kind)
        else:
            kind_id = kind

        new_coin = Coin(date=date, time_block=time_block,
                        behavior_id=behavior_id, remark_id=remark_id, kind_id=kind_id, rowspan=rowspan)

        session.add(new_coin)
        session.commit()
        session.refresh(new_coin)
        session.close()

        return new_coin.id

    def edit_coin(self, coin_id, date_new=None, time_block_new=None, behavior_new=None,
                  remark_new=None, kind_new=None, rowspan_new=None):
        pass

    def get_coin_id(self, time, behavior):
        # todo find time_block in the row span
        # time -> date + time_block
        pass

    def add_behavior(self, name):
        session = self.sessionmaker()
        behavior_id = self.get_behavior_id(name)
        if behavior_id is None:
            new_behavior = Behavior(name=name)
            session.add(new_behavior)
            session.commit()
            session.refresh(new_behavior)
            behavior_id = new_behavior.id

        session.close()
        return behavior_id

    def edit_behavior(self, behavior_id, name_new=None):
        pass

    def get_behavior_id(self, name):
        session = self.sessionmaker()
        behavior = session.query(Behavior).filter_by(name=name).first()
        session.close()

        if behavior is None:
            return None
        else:
            return behavior.id

    def add_remark(self, name):
        session = self.sessionmaker()
        remark_id = self.get_remark_id(name)
        if remark_id is None:
            new_remark = Remark(name=name)
            session.add(new_remark)
            session.commit()
            session.refresh(new_remark)
            #id_query = session.query(Remark).filter_by(name=name).first()
            #remark_id = id_query.id
            remark_id = new_remark.id

        session.close()
        return remark_id

    def edit_remark(self, remark_id, name_new=None):
        pass

    def get_remark_id(self, name):
        session = self.sessionmaker()
        remark = session.query(Remark).filter_by(name=name).first()
        session.close()

        if remark is None:
            return None
        else:
            return remark.id

    def add_kind(self, name, color_id):
        session = self.sessionmaker()

        kind_id = self.get_kind_id(name)
        if kind_id is None:
            new_kind = Kind(name=name, color_id=color_id)
            session.add(new_kind)
            session.commit()
            session.refresh(new_kind)
            kind_id = new_kind.id

        session.close()
        return kind_id

    def edit_kind(self, kind_id, name_new=None, color_new=None):
        pass

    def get_kind_id(self, name):
        session = self.sessionmaker()
        kind = session.query(Kind).filter_by(name=name).first()
        session.close()
        if kind is None:
            return None
        else:
            return kind.id

    def add_color(self, color=None, name=''):
        # color is string = hex code
        # color is tuple = (r, g, b) code
        session = self.sessionmaker()

        if isinstance(color, tuple):
            hex = self.rgb2hex(color)
        else:
            hex = color

        color_id = self.get_color_id(hex)
        if color_id is None:
            new_color = Color(hex=hex, name=name)
            session.add(new_color)
            session.commit()
            color_id = self.get_color_id(hex)
        else:
            print('[Warning]: This color already exists!')

        session.close()
        return color_id

    def edit_color(self, color_id, name_new=None, color_new=None):
        pass

    def get_color_id(self, color):
        session = self.sessionmaker()
        if isinstance(color, tuple):  # select by rgb
            color = self.rgb2hex(color)

        if '#' in color:   # hex mode
            color_query = session.query(Color).filter_by(hex=color).first()
        else:    # name mode
            color_query = session.query(Color).filter_by(name=color).first()

        session.close()

        if color_query is None:
            return None
        else:
            return color_query.id

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
    db = DBOperator(db_name)
    if not os.path.exists(db_name):
        db.create_db()
    # test behavior
    test_behavior_id0 = db.add_behavior('rua')
    test_behavior_id1 = db.add_behavior('rua')   # test_duplicate
    test_behavior_id2 = db.get_behavior_id('rua')
    ### todo test-edit

    # test remark
    test_remark_id0 = db.add_remark('remark')
    test_remark_id1 = db.add_remark('remark')   # test_duplicate
    test_remark_id2 = db.get_remark_id('remark')
    ### todo test-edit

    # test color
    test_color_id0 = db.add_color(color=(210, 223, 224), name='淡灰')   # this already exist when create db
    test_color_id1 = db.get_color_id(color=(210, 223, 224))
    test_color_id2 = db.get_color_id(color='淡灰')
    ### todo test-edit

    # test kind
    test_kind_id0 = db.add_kind(name='尽情娱乐', color_id=db.get_color_id('天蓝'))
    test_kind_id1 = db.get_kind_id(name='尽情娱乐')

    # test coin
    db.add_coin(date=20190817, time_block=1, behavior='rua', remark=1, kind=1)
    db.add_coin(date=20190817, time_block=2, behavior='rua2', remark=1, kind=2, rowspan=2)
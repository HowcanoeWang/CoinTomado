# -*- coding: utf-8 -*-
import os
import sqlite3
import logging
import datetime
from config import Config


class DB(object):
<<<<<<< HEAD
    models = {'DAYS': {}, 'WEEKS': {}, 'MONTHS':{}}
    
    models['DAYS'] = {'tablename': 'DAYS',
                      'column': 'ID, fun, rest, work, compel, useless, \
                                 sleep, sleep_st, sleep_ed, frequency',
                      'attr': '''(ID        INT   NOT NULL    PRIMARY KEY,
                                 fun       REAL   NOT NULL,
                                 rest      REAL   NOT NULL,
                                 work      REAL   NOT NULL,
                                 compel    REAL   NOT NULL,
                                 useless   REAL   NOT NULL,
                                 sleep     REAL   NOT NULL,
                                 sleep_st  REAL,
                                 sleep_ed  REAL,        
                                 frequency CHAR(80))'''}
    
    models['WEEKS'] = {'tablename': 'WEEKS',
                       'column': 'ID, fun, rest, work, compel, useless, sleep, \
                                  sleep_st, sleep_ed, frequency, notes',
                       'attr':'''(ID        INT   NOT NULL    PRIMARY KEY,
                                 fun       REAL   NOT NULL,
                                 rest      REAL   NOT NULL,
                                 work      REAL   NOT NULL,
                                 compel    REAL   NOT NULL,
                                 useless   REAL   NOT NULL,
                                 sleep     REAL   NOT NULL,
                                 sleep_st  REAL,
                                 sleep_ed  REAL,        
                                 frequency CHAR(80),
                                 notes     CHAR(512))'''}

    models['MONTHS'] = {'tablename': 'MONTHS',
                        'column': 'ID, fun, rest, work, compel, useless, sleep, \
                                   sleep_st, sleep_ed, frequency',
                        'attr':'''(ID        INT   NOT NULL    PRIMARY KEY,
                                  fun       REAL   NOT NULL,
                                  rest      REAL   NOT NULL,
                                  work      REAL   NOT NULL,
                                  compel    REAL   NOT NULL,
                                  useless   REAL   NOT NULL,
                                  sleep     REAL   NOT NULL,
                                  sleep_st  REAL,
                                  sleep_ed  REAL,        
                                  frequency CHAR(80))'''} 

    def __init__(self, conn, modelname):     
        self.conn = conn
=======
    db_path = 'default.db'
    __tablename__ = 'COMPANY'
    __column__ = 'ID, NAME, AGE, ADDRESS, SALARY'
    init_str = 'CREATE TABLE ' + __tablename__ + '''
                (ID      INT       NOT NULL    PRIMARY KEY,
                 Name    TEXT      NOT NULL,
                 AGE     INT       NOT NULL,
                 ADDRESS CHAR(50),
                 SALARY  REAL);'''

    def __init__(self, db_path='default.db'):
        self.db_path = db_path
        init = False
        if not os.path.exists(db_path):
            init = True
        self.conn = sqlite3.connect(self.db_path)
        logging.info('Open database [' + self.db_path + '] successfully')
>>>>>>> parent of 5763562... Sqlite3 models finished
        self.c = self.conn.cursor()
        self.__tablename__ = self.models[modelname]['tablename']
        self.__column__ = self.models[modelname]['column']
        self.__attr__ = self.models[modelname]['attr']

        if init:
            self._initialize()

    def _initialize(self):
<<<<<<< HEAD
        sql = 'CREATE TABLE ' + self.__tablename__ + self.__attr__
        try:
            self.c.execute(sql)
            logging.info('table ' + self.__tablename__ + ' has been created')
            self.commit()
        except:
            logging.exception(sql)
=======
        self.c.execute(self.init_str)
        logging.info('Table ' + self.__tablename__ + ' created successfully')
>>>>>>> parent of 5763562... Sqlite3 models finished
        pass

    def _insert(self, value_tuple):
        sql = 'INSERT INTO ' + self.__tablename__ + '(' + self.__column__ + ') VALUES' + str(value_tuple)
        try:
            self.c.execute(sql)
        except sqlite3.OperationalError:
            logging.error('sqlite3.OperationalError: unrecognized token:' + sql)

    def _update(self, value_tuple):
        column_name = self.__column__.split(', ')
        set_str = ''
        for i, col in enumerate(column_name):
            if i == 0:   # skip id
                continue
            if isinstance(value_tuple[i], str):  # string add "" into SQL command
                set_str += col + ' = "' + str(value_tuple[i]) + '"'
            else:    # not string use str() directly
                set_str += col + ' = ' + str(value_tuple[i])
            if i < len(column_name) - 1:   # add , except last element
                set_str += ', '
        sql = 'UPDATE ' + self.__tablename__ + ' SET ' + set_str + ' WHERE ID = ' + str(value_tuple[0])
        try:
            self.c.execute(sql)
        except sqlite3.OperationalError:
            logging.error('sqlite3.OperationalError: unrecognized token:' + sql)

    def _select(self, column_names, id_tuple=None):
        pass

    def add(self, value_tuple):
        cursor = self.conn.execute('SELECT id from ' + self.__tablename__ +
                                   ' WHERE ID=' + str(value_tuple[0])).fetchall()
        if len(cursor) == 0:  # no result, use insert
            self._insert(value_tuple)
        else:  # have record, use update
            self._update(value_tuple)

    def drop_table(self):
        pass

    def commit(self):
        self.conn.commit()
<<<<<<< HEAD
        

if __name__ == '__main__':
    cfg = Config()
    db_path = cfg.cache_dir + '/weekery.db'
    init = False
    if not os.path.exists(db_path):
        init = True

    conn = sqlite3.connect(db_path)
    days = DB(conn, 'DAYS')
    weeks = DB(conn, 'WEEKS')
    months = DB(conn, 'MONTHS')
=======


class Days(DB):
    pass


class Weeks(DB):
    pass


class Months(DB):
    pass


if __name__ == '__main__':
    cfg = Config()
    db = DB(cfg.cache_dir + '/weekery.db')
>>>>>>> parent of 5763562... Sqlite3 models finished

    t = datetime.datetime.now()
    # for i in range(1000):
    #     db.insert((i, 'Paul', 32, 'California', 20000.00))
    #
    db.add((3, "Paul", 32, "California", 10000.00))
    db.add((3000, 'Paul', 32, 'California', 30000.00))
    db.commit()
    print(datetime.datetime.now() - t)
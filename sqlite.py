# -*- coding: utf-8 -*-
import os
import sqlite3
import logging
import datetime
from config import Config


class DB(object):
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
        self.c = self.conn.cursor()
        self.__tablename__ = self.models[modelname]['tablename']
        self.__column__ = self.models[modelname]['column']
        self.__attr__ = self.models[modelname]['attr']

    def _initialize(self):
        sql = 'CREATE TABLE ' + self.__tablename__ + self.__attr__
        try:
            self.c.execute(sql)
            logging.info('table ' + self.__tablename__ + ' has been created')
            self.commit()
        except:
            logging.exception(sql)
        pass

    def _insert(self, value_tuple):
        sql = 'INSERT INTO ' + self.__tablename__ + '(' + self.__column__ + ') VALUES' + str(value_tuple)
        try:
            self.c.execute(sql)
        except:
            logging.exception(sql)

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
        except:
            logging.exception(sql)

    def _select(self, column_str, id_tuple):
        # column_str = 'ID, NAME, AGE, ADDRESS, SALARY'
        sql = 'SELECT ' + column_str + ' FROM ' + self.__tablename__ + \
              ' WHERE ID BETWEEN ' + str(id_tuple[0]) + ' AND ' + str(id_tuple[-1])
        try:
            result = self.c.execute(sql).fetchall()
            return result
        except:
            logging.exception(sql)

    def add(self, value_tuple):
        sql = 'SELECT id from ' + self.__tablename__ + ' WHERE ID=' + str(value_tuple[0])
        try:
            cursor = self.conn.execute(sql).fetchall()
            if len(cursor) == 0:  # no result, use insert
                self._insert(value_tuple)
            else:  # have record, use update
                self._update(value_tuple)
        except:
            logging.exception(sql)

    def drop_table(self):
        pass

    def commit(self):
        self.conn.commit()
        

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

    t = datetime.datetime.now()

    if init:
        days._initialize()
        weeks._initialize()
        months._initialize()


    days.add((20170120, 5, 6, 3, 2, 1, 5, -1.5, 6.0, "{'a':1, 'b':2, 'c':3}"))
    weeks.add((20170120, 5, 6, 3, 2, 1, 5, 2.5, 6.0, "{'a':1, 'b':2, 'c':3}", 'asdfasdfwefsdfsedfsdf'))

    da_r = days._select('ID, fun, rest, work, compel, useless, sleep, frequency', (20170100, 20180100))
    we_r = weeks._select('ID, fun, rest, work, compel, useless, sleep, frequency, notes', (20170100, 20180100))


    print(da_r)
    print(we_r)

    days.commit()
    print(datetime.datetime.now() - t)
    conn.close()
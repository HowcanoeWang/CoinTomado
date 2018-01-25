# -*- coding: utf-8 -*-
import os
import sqlite3
import logging
import datetime
from config import Config


class DB(object):
    __tablename__ = 'COMPANY'
    __column__ = 'ID, NAME, AGE, ADDRESS, SALARY'
    init_str = 'CREATE TABLE ' + __tablename__ + '''
                (ID      INT       NOT NULL    PRIMARY KEY,
                 Name    TEXT      NOT NULL,
                 AGE     INT       NOT NULL,
                 ADDRESS CHAR(50),
                 SALARY  REAL);'''

    def __init__(self, conn):
        self.conn = conn
        self.c = self.conn.cursor()

    def _initialize(self):
        try:
            self.c.execute(self.init_str)
            logging.info('table ' + self.__tablename__ + ' has been created')
            self.commit()
        except:
            logging.exception(self.init_str)
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


class Days(DB):
    __tablename__ = 'DAYS'
    __column__ = 'ID, fun, rest, work, compel, useless, sleep, sleep_st, sleep_ed, frequency'
    init_str = 'CREATE TABLE ' + __tablename__ + '''
                (ID        INT   NOT NULL    PRIMARY KEY,
                 fun       REAL   NOT NULL,
                 rest      REAL   NOT NULL,
                 work      REAL   NOT NULL,
                 compel    REAL   NOT NULL,
                 useless   REAL   NOT NULL,
                 sleep     REAL   NOT NULL,
                 sleep_st  REAL,
                 sleep_ed  REAL,        
                 frequency CHAR(80));'''
    """
    from collections import Counter
    >>> A = Counter({'a':1, 'b':2, 'c':3})
    >>> B = Counter({'b':3, 'c':4, 'd':5})
    >>> A + B
    Counter({'c': 7, 'b': 5, 'd': 5, 'a': 1})
    """


class Weeks(DB):
    __tablename__ = 'WEEKS'
    __column__ = 'ID, fun, rest, work, compel, useless, sleep, sleep_st, sleep_ed, frequency, notes'
    init_str = 'CREATE TABLE ' + __tablename__ + '''
                (ID        INT   NOT NULL    PRIMARY KEY,
                 fun       REAL   NOT NULL,
                 rest      REAL   NOT NULL,
                 work      REAL   NOT NULL,
                 compel    REAL   NOT NULL,
                 useless   REAL   NOT NULL,
                 sleep     REAL   NOT NULL,
                 sleep_st  REAL,
                 sleep_ed  REAL,        
                 frequency CHAR(80),
                 notes     CHAR(512));'''

class Months(DB):
    __tablename__ = 'MONTHS'
    __column__ = 'ID, fun, rest, work, compel, useless, sleep, sleep_st, sleep_ed, frequency'
    init_str = 'CREATE TABLE ' + __tablename__ + '''
                    (ID        INT   NOT NULL    PRIMARY KEY,
                     fun       REAL   NOT NULL,
                     rest      REAL   NOT NULL,
                     work      REAL   NOT NULL,
                     compel    REAL   NOT NULL,
                     useless   REAL   NOT NULL,
                     sleep     REAL   NOT NULL,
                     sleep_st  REAL,
                     sleep_ed  REAL,        
                     frequency CHAR(80));'''


if __name__ == '__main__':
    cfg = Config()
    db_path = cfg.cache_dir + '/weekery.db'
    init = False
    if not os.path.exists(db_path):
        init = True

    conn = sqlite3.connect(db_path)
    days = Days(conn)
    weeks = Weeks(conn)
    months = Months(conn)

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
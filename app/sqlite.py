# -*- coding: utf-8 -*-
import sqlite3
import logging
import datetime
from config import Config


class DB(object):
    models = {'DAYS': {}, 'WEEKS': {}, 'MONTHS': {}, 'YEARS': {}}

    models['DAYS'] = {'tablename': 'DAYS',
                      'column': 'ID, fun, rest, work, compel, useless, \
                                 sleep, sleep_st, sleep_ed, frequency',
                      'attr': '''(ID        INT   NOT NULL    PRIMARY KEY,
                                  fun       REAL,
                                  rest      REAL,
                                  work      REAL,
                                  compel    REAL,
                                  useless   REAL,
                                  sleep     REAL,
                                  sleep_st  REAL,
                                  sleep_ed  REAL,        
                                  frequency CHAR(512))'''}
    
    models['WEEKS'] = {'tablename': 'WEEKS',
                       'column': 'ID, fun, rest, work, compel, useless, sleep, \
                                  sleep_st, sleep_ed, frequency, notes',
                       'attr': '''(ID        INT   NOT NULL    PRIMARY KEY,
                                   fun       REAL,
                                   rest      REAL,
                                   work      REAL,
                                   compel    REAL,
                                   useless   REAL,
                                   sleep     REAL,
                                   sleep_st  REAL,
                                   sleep_ed  REAL,        
                                   frequency CHAR(512),
                                   notes     CHAR(512))'''}

    models['MONTHS'] = {'tablename': 'MONTHS',
                        'column': 'ID, fun, rest, work, compel, useless, sleep, \
                                   sleep_st, sleep_ed, frequency',
                        'attr': '''(ID        INT   NOT NULL    PRIMARY KEY,
                                    fun       REAL,
                                    rest      REAL,
                                    work      REAL,
                                    compel    REAL,
                                    useless   REAL,
                                    sleep     REAL,
                                    sleep_st  REAL,
                                    sleep_ed  REAL,        
                                    frequency CHAR(512))'''}
    
    models['YEARS'] = {'tablename': 'YEARS',
                       'column': 'ID, fun, rest, work, compel, useless, sleep, \
                                  sleep_st, sleep_ed, frequency',
                       'attr': '''(ID        INT   NOT NULL    PRIMARY KEY,
                                   fun       REAL,
                                   rest      REAL,
                                   work      REAL,
                                   compel    REAL,
                                   useless   REAL,
                                   sleep     REAL,
                                   sleep_st  REAL,
                                   sleep_ed  REAL,        
                                   frequency CHAR(512))'''}

    def __init__(self, conn, modelname):     
        self.conn = conn
        self.c = self.conn.cursor()
        self.__tablename__ = self.models[modelname]['tablename']
        self.__column__ = self.models[modelname]['column']
        self.__attr__ = self.models[modelname]['attr']
        sql = 'SELECT * FROM ' + self.__tablename__
        try:
            self.c.execute(sql)
        except sqlite3.OperationalError:
            self._initialize()

    def _initialize(self):
        sql = 'CREATE TABLE ' + self.__tablename__ + self.__attr__
        try:
            self.c.execute(sql)
            logging.info('table ' + self.__tablename__ + ' has been created')
            self.conn.commit()
        except Exception:
            logging.exception(sql)

    def _insert(self, value_tuple, column='self.__column__'):
        sql = 'INSERT INTO ' + self.__tablename__ + '(' + column + ') VALUES' + str(value_tuple)
        try:
            self.c.execute(sql)
        except Exception:
            logging.exception(sql)

    def _update(self, value_tuple, column='self.__column__'):
        column_name = column.split(', ')
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
        except Exception:
            logging.exception(sql)

    def select(self, column_str, id_tuple):
        # column_str = 'ID, NAME, AGE, ADDRESS, SALARY'
        sql = 'SELECT ' + column_str + ' FROM ' + self.__tablename__ + \
              ' WHERE ID BETWEEN ' + str(id_tuple[0]) + ' AND ' + str(id_tuple[-1])
        try:
            result = self.c.execute(sql).fetchall()
            return result
        except Exception:
            logging.exception(sql)

    def add(self, value_tuple, column='self.__column__'):
        sql = 'SELECT id from ' + self.__tablename__ + ' WHERE ID=' + str(value_tuple[0])
        if column == 'self.__column__':
            column = self.__column__
        try:
            cursor = self.conn.execute(sql).fetchall()
            if len(cursor) == 0:  # no result, use insert
                self._insert(value_tuple, column)
            else:  # have record, use update
                self._update(value_tuple, column)
        except Exception:
            logging.exception(sql)

    def drop_table(self):
        pass


if __name__ == '__main__':
    Cfg = Config()
    db_path = Cfg.cache_dir + '/weekery.db'

    Conn = sqlite3.connect(db_path)
    days = DB(Conn, 'DAYS')
    weeks = DB(Conn, 'WEEKS')
    months = DB(Conn, 'MONTHS')

    t = datetime.datetime.now()

    days.add((20170120, 5, 6, 3, 2, 1, 5, -1.5, 6.0, "{'a':1, 'b':2, 'c':3}"))
    weeks.add((20170120, 5, 6, 3, 2, 1, 5, 2.5, 6.0, "{'a':1, 'b':2, 'c':3}", 'asdfasdfwefsdfsedfsdf'))
    print(days.select('ID, fun, rest, work, compel, useless, sleep, frequency', (20170100, 20180100)))
    
    # specified test
    days.add((20170121, "{'a':1, 'b':4, 'c':5}"), column='ID, frequency')
    days.add((20170123, -2.5), column='ID, sleep_st')
    print(days.select('ID, fun, rest, work, compel, useless, sleep, frequency', (20170100, 20180100)))
    # null test
    days.add((20170110, 5, 6, 7, 8, 9, 2), 'ID, fun, rest, work, compel, useless, sleep')
    print(days.select('ID, fun, rest, work, compel, useless, sleep, frequency', (20170100, 20180100)))
    
    we_r = weeks.select('ID, fun, rest, work, compel, useless, sleep, frequency, notes', (20170100, 20180100))

    print(we_r)

    Conn.commit()
    print(datetime.datetime.now() - t)
    Conn.close()
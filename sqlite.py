# -*- coding: utf-8 -*-
import os
import sqlite3
import logging
import datetime
from config import Config


class DB(object):
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
        self.c = self.conn.cursor()

        if init:
            self._initialize()

    def _initialize(self):
        self.c.execute(self.init_str)
        logging.info('Table ' + self.__tablename__ + ' created successfully')
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


class Days(DB):
    pass


class Weeks(DB):
    pass


class Months(DB):
    pass


if __name__ == '__main__':
    cfg = Config()
    db = DB(cfg.cache_dir + '/weekery.db')

    t = datetime.datetime.now()
    # for i in range(1000):
    #     db.insert((i, 'Paul', 32, 'California', 20000.00))
    #
    db.add((3, "Paul", 32, "California", 10000.00))
    db.add((3000, 'Paul', 32, 'California', 30000.00))
    db.commit()
    print(datetime.datetime.now() - t)
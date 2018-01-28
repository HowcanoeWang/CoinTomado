import datetime
import calendar
import sqlite3
from sqlite import DB
from config import Config


class Controls(object):
    y = int(datetime.datetime.now().year)
    m = int(datetime.datetime.now().month)
    w = int(datetime.datetime.now().strftime("%W"))
    d = int(datetime.datetime.now().strftime("%d"))
    n = 7
    mod = 'WEEKS'

    def __init__(self, conn):
        self.mod = 'WEEKS'
        self._date_range()
        self.conn = conn

    def _add_months(self, source_date, months):
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(source_date.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)
    
    def _date_range(self):
        if self.mod == 'DAYS':
            self.ed = datetime.date(self.y, self.m, self.d)
            self.st = self.ed - datetime.timedelta(days=self.n-1)
        elif self.mod == 'WEEKS':
            now = datetime.date(self.y, self.m, self.d)
            st_this_week = now - datetime.timedelta(days=now.weekday())
            ed_this_week = st_this_week + datetime.timedelta(days=6)
            self.ed = ed_this_week
            self.st = st_this_week - datetime.timedelta(weeks=self.n-1)
        elif self.mod == 'MONTHS':
            st_this_month = datetime.date(self.y, self.m, 1)
            ed_this_month = self._add_months(st_this_month, 1) - datetime.timedelta(days=1)
            self.ed = ed_this_month
            self.st = self._add_months(st_this_month, - (self.n - 1))
        elif self.mod == 'YEARS':
            self.ed = datetime.date(self.y,12,31)
            self.st = datetime.date(self.y - (self.n - 1), 1, 1)
        else:
            pass
    
    def _query_data(self):
        table = DB(self.conn, self.mod)
        st = int(self.st.strftime('%Y%m%d'))
        ed = int(self.ed.strftime('%Y%m%d'))
        # query for plot data
        query = table._select('ID, fun, rest, work, compel, useless, sleep, sleep_st, sleep_ed, frequency',
                             (st, ed))
        for item in query:
            print(item)
        # query for notes data
        weeks = DB(self.conn, 'WEEKS')
        now = datetime.date(self.y, self.m, self.d)
        st_this_week = now - datetime.timedelta(days=now.weekday())
        ed_this_week = st_this_week + datetime.timedelta(days=6)
        w_st = int(st_this_week.strftime('%Y%m%d'))
        w_ed = int(ed_this_week.strftime('%Y%m%d'))
        note = weeks._select('ID, notes', (w_st, w_ed))
        print(note)

    def days(self):
        self.mod = 'DAYS'
        self._date_range()
        self._query_data()

    def weeks(self):
        self.mod = 'WEEKS'
        self._date_range()
        self._query_data()

    def months(self):
        self.mod = 'MONTHS'
        self._date_range()
        self._query_data()

    def years(self):
        self.mod = 'YEARS'
        self._date_range()
        self._query_data()

    def previous(self):
        if self.mod == 'DAYS':
            now = datetime.date(self.y, self.m, self.d)
            previous = now - datetime.timedelta(days=1)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self._date_range()
        elif self.mod == 'WEEKS':
            now = datetime.date(self.y, self.m, self.d)
            previous = now - datetime.timedelta(weeks=1)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self._date_range()
        elif self.mod == 'MONTHS':
            now = datetime.date(self.y, self.m, self.d)
            previous = self._add_months(now, -1)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self._date_range()
        elif self.mod == 'YEARS':
            now = datetime.date(self.y, self.m, self.d)
            previous = now - datetime.timedelta(days=365)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self._date_range()
        else:
            pass
        self._query_data()

    def backward(self):
        if self.mod == 'DAYS':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = now + datetime.timedelta(days=1)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self._date_range()
        elif self.mod == 'WEEKS':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = now + datetime.timedelta(days=1)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self._date_range()
        elif self.mod == 'MONTHS':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = self._add_months(now, 1)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self._date_range()
        elif self.mod == 'YEARS':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = now + datetime.timedelta(days=365)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self._date_range()
        else:
            pass
        self._query_data()

    def plus(self):
        self.n += 1
        self._date_range()
        self._query_data()

    def minus(self):
        if self.n - 1 > 0:
            self.n -= 1
            self._date_range()
            self._query_data()
        else:
            print("Minimum number has been met!")
        

if __name__ == '__main__':
    cfg = Config()
    db_path = cfg.cache_dir + '/weekery.db'

    conn = sqlite3.connect(db_path)

    ctrl = Controls(conn)
    loop = True
    while loop:
        print('>>>', ctrl.y, ctrl.m, ctrl.d, '[W'+str(ctrl.w)+'], Mod:'+ctrl.mod, 'n='+str(ctrl.n),
              '\n>>> ShowRange:[', ctrl.st.strftime('%Y%m%d'), ',', ctrl.ed.strftime('%Y%m%d'), ']')
        cmd = input('Please input command [d, w, m, <, >, +, -, q]: ')
        if cmd == 'd':
            ctrl.days()
        elif cmd == 'w':
            ctrl.weeks()
        elif cmd == 'm':
            ctrl.months()
        elif cmd == 'y':
            ctrl.years()
        elif cmd == '-':
            ctrl.minus()
        elif cmd == '+':
            ctrl.plus()
        elif cmd == '<':
            ctrl.previous()
        elif cmd == '>':
            ctrl.backward()
        elif cmd == 'q':
            loop = False
        else:
            print('No such command')

    conn.close()

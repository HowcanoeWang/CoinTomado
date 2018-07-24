import datetime
import calendar
from collections import Counter
import sqlite3
import pandas as pd
import logging
from sqlite import DB
from config import Config
from dateutil.relativedelta import relativedelta


class Controls(object):
    y = int(datetime.datetime.now().year)
    m = int(datetime.datetime.now().month)
    w = int(datetime.datetime.now().strftime("%W"))
    d = int(datetime.datetime.now().strftime("%d"))
    n = 7
    mod = 'DAYS'
    kinds = None
    sleep_condition = None
    frequency = None
    notes = None

    def __init__(self, conn):
        self.mod = 'DAYS'
        # self.date_range()
        now = datetime.date(self.y, self.m, self.d)
        self.st = now - datetime.timedelta(days=now.weekday())
        self.ed = self.st + datetime.timedelta(days=6)
        self.conn = conn
        self.query_data()

    @staticmethod
    def _add_months(source_date, months):
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(source_date.day, calendar.monthrange(year, month)[1])

        return datetime.date(year, month, day)
    
    def date_range(self):
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
            self.ed = datetime.date(self.y, 12, 31)
            self.st = datetime.date(self.y - (self.n - 1), 1, 1)
        else:
            pass
    
    def query_data(self):
        table = DB(self.conn, self.mod)
        st = int(self.st.strftime('%Y%m%d'))
        ed = int(self.ed.strftime('%Y%m%d'))
        # generate date_range
        index_range = []
        if self.mod == 'DAYS':
            index_range = [(self.st + datetime.timedelta(days=x)).strftime('%y-%m-%d')
                           for x in range(0, (self.ed - self.st).days + 1)]
        elif self.mod == 'WEEKS':
            w_st = self.st
            w_ed = self.ed
            while w_st <= w_ed:
                index_range.append(w_st.strftime('%yW%W'))
                w_st += datetime.timedelta(days=7)
        elif self.mod == 'MONTHS':
            m_st = self.st
            m_ed = self.ed
            while m_st <= m_ed:
                index_range.append(m_st.strftime('%Y-%m'))
                m_st += relativedelta(months=1)
        elif self.mod == 'YEARS':
            y_st = int(self.st.strftime('%Y%m%d')[:4])
            y_ed = int(self.ed.strftime('%Y%m%d')[:4])
            index_range = [str(i) for i in range(y_st, y_ed+1)]
        else:
            return
        # initialize dataframe
        kinds = pd.DataFrame(0.0, index=index_range, columns=['fun', 'rest', 'work', 'compel', 'useless', 'sleep'])
        frequency = {'Summary':[[],[]]}
        frequency_summary = Counter({})
        sleep_condition = pd.DataFrame(None, index=index_range, columns=['sleep_st', 'sleep_ed'])

        # query for plot data
        query = table.select('ID, fun, rest, work, compel, useless, sleep, sleep_st, sleep_ed, frequency',
                              (st, ed))

        date_str = '1995'
        record = True
        for item in reversed(query):
            date = datetime.datetime.strptime(str(item[0]),'%Y%m%d')
            if self.mod == 'DAYS':
                date_str = date.strftime('%y-%m-%d')
            elif self.mod == 'WEEKS':
                date_str = date.strftime('%yW%W')
            elif self.mod == 'MONTHS':
                date_str = date.strftime('%Y-%m')
            elif self.mod == 'YEARS':
                date_str = date.strftime('%Y')
            else:
                return

            if date_str in index_range:
                # kinds
                kinds.loc[date_str] = item[1:7]
                # sleep_condition
                if item[8] is not None:
                    sleep_condition.loc[date_str] = item[7:9]
                # frequency
                if item[-1] is not None:
                    freq_dict = eval(item[-1])
                    freq_counter = Counter(freq_dict)
                    frequency_summary += freq_counter
                    if len(freq_dict.keys()) >= 1 and record == True:
                        frequency[date_str] = [list(freq_dict.keys()), list(freq_dict.values())]
                        record=False
            else:
                logging.info(date_str + 'not in ' + str(index_range))

        #frequen = dict(frequency_summary.most_common(10))
        frequen = dict(frequency_summary)
        frequency['Summary'] = [list(frequen.keys()), list(frequen.values())]

        # query for notes data
        weeks = DB(self.conn, 'WEEKS')
        now = datetime.date(self.y, self.m, self.d)
        st_this_week = now - datetime.timedelta(days=now.weekday())
        ed_this_week = st_this_week + datetime.timedelta(days=6)
        w_st = int(st_this_week.strftime('%Y%m%d'))
        w_ed = int(ed_this_week.strftime('%Y%m%d'))
        notes_select = weeks.select('ID, notes', (w_st, w_ed))
        if len(notes_select) > 0:
            notes = [datetime.datetime.strptime(str(notes_select[0][0]), '%Y%m%d').strftime('%yW%W'), notes_select[0][-1]]
        else:
            notes = [None, '']
        self.kinds = kinds
        self.sleep_condition = sleep_condition
        self.frequency = frequency
        self.notes = notes

    def days(self):
        self.mod = 'DAYS'
        self.date_range()
        self.query_data()

    def weeks(self):
        self.mod = 'WEEKS'
        self.date_range()
        self.query_data()

    def months(self):
        self.mod = 'MONTHS'
        self.date_range()
        self.query_data()

    def years(self):
        self.mod = 'YEARS'
        self.date_range()
        self.query_data()

    def previous(self):
        if self.mod == 'DAYS':
            now = datetime.date(self.y, self.m, self.d)
            previous = now - datetime.timedelta(days=1)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self.date_range()
        elif self.mod == 'WEEKS':
            now = datetime.date(self.y, self.m, self.d)
            previous = now - datetime.timedelta(weeks=1)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self.date_range()
        elif self.mod == 'MONTHS':
            now = datetime.date(self.y, self.m, self.d)
            previous = self._add_months(now, -1)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self.date_range()
        elif self.mod == 'YEARS':
            now = datetime.date(self.y, self.m, self.d)
            previous = now - datetime.timedelta(days=365)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self.date_range()
        else:
            pass
        self.query_data()

    def backward(self):
        if self.mod == 'DAYS':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = now + datetime.timedelta(days=1)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self.date_range()
        elif self.mod == 'WEEKS':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = now + datetime.timedelta(weeks=1)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self.date_range()
        elif self.mod == 'MONTHS':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = self._add_months(now, 1)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self.date_range()
        elif self.mod == 'YEARS':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = now + datetime.timedelta(days=365)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self.date_range()
        else:
            pass
        self.query_data()

    def plus(self):
        if self.n < 8:
            self.n += 1
            self.date_range()
            self.query_data()
        else:
            print('Maximum number has been met!')


    def minus(self):
        if self.n - 1 > 0:
            self.n -= 1
            self.date_range()
            self.query_data()
        else:
            print("Minimum number has been met!")
        

if __name__ == '__main__':
    cfg = Config('root')
    db_path = cfg.cache_dir + '/weekery.db'

    Conn = sqlite3.connect(db_path)

    ctrl = Controls(Conn)
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

    Conn.close()

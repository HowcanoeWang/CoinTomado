import datetime
import calendar


class Controls(object):
    y = int(datetime.datetime.now().year)
    m = int(datetime.datetime.now().month)
    w = int(datetime.datetime.now().strftime("%W"))
    d = int(datetime.datetime.now().strftime("%d"))
    n = 7
    mod = 'w'

    def __init__(self):
        self.mod = 'w'
        self._date_range()

    def _add_months(self, source_date, months):
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(source_date.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)
    
    def _date_range(self):
        if self.mod == 'd':
            self.ed = datetime.date(self.y, self.m, self.d)
            self.op = self.ed - datetime.timedelta(days=self.n-1)
        elif self.mod == 'w':
            now = datetime.date(self.y, self.m, self.d)
            st_this_week = now - datetime.timedelta(days=now.weekday())
            ed_this_week = st_this_week + datetime.timedelta(days=6)
            self.ed = ed_this_week
            self.op = st_this_week - datetime.timedelta(weeks=self.n-1)
        elif self.mod == 'm':
            st_this_month = datetime.date(self.y, self.m, 1)
            ed_this_month = self._add_months(st_this_month, 1) - datetime.timedelta(days=1)
            self.ed = ed_this_month
            self.op = self._add_months(st_this_month, - (self.n - 1))
        elif self.mod == 'y':
            self.ed = datetime.date(self.y,12,31)
            self.op = datetime.date(self.y - (self.n - 1), 1, 1)
        else:
            pass

    def days(self):
        self.mod = 'd'
        self._date_range()

    def weeks(self):
        self.mod = 'w'
        self._date_range()

    def months(self):
        self.mod = 'm'
        self._date_range()

    def years(self):
        self.mod = 'y'
        self._date_range()

    def previous(self):
        if self.mod == 'd':
            now = datetime.date(self.y, self.m, self.d)
            previous = now - datetime.timedelta(days=1)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self._date_range()
        elif self.mod == 'w':
            now = datetime.date(self.y, self.m, self.d)
            previous = now - datetime.timedelta(weeks=1)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self._date_range()
        elif self.mod == 'm':
            now = datetime.date(self.y, self.m, self.d)
            previous = self._add_months(now, -1)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self._date_range()
        elif self.mod == 'y':
            now = datetime.date(self.y, self.m, self.d)
            previous = now - datetime.timedelta(days=365)
            self.y = int(previous.year)
            self.m = int(previous.month)
            self.d = int(previous.strftime('%d'))
            self.w = int(previous.strftime('%W'))
            self._date_range()
        else:
            pass

    def next(self):
        if self.mod == 'd':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = now + datetime.timedelta(days=1)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self._date_range()
        elif self.mod == 'w':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = now + datetime.timedelta(days=1)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self._date_range()
        elif self.mod == 'm':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = self._add_months(now, 1)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self._date_range()
        elif self.mod == 'y':
            now = datetime.date(self.y, self.m, self.d)
            afterwards = now + datetime.timedelta(days=365)
            self.y = int(afterwards.year)
            self.m = int(afterwards.month)
            self.d = int(afterwards.strftime('%d'))
            self.w = int(afterwards.strftime('%W'))
            self._date_range()
        else:
            pass

    def plus(self):
        self.n += 1
        self._date_range()

    def minus(self):
        if self.n - 1 > 0:
            self.n -= 1
            self._date_range()
        else:
            print("Minimum number has been met!")
        

if __name__ == '__main__':
    ctrl = Controls()
    loop = True
    while loop:
        print('>>>', ctrl.y, ctrl.m, ctrl.d, '[W'+str(ctrl.w)+'], Mod:'+ctrl.mod, 'n='+str(ctrl.n),
              '\n>>> ShowRange:[', ctrl.op.strftime('%Y%m%d'), ',', ctrl.ed.strftime('%Y%m%d'), ']')
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
            ctrl.next()
        elif cmd == 'q':
            loop = False
        else:
            print('No such command')

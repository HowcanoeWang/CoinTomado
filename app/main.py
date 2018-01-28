# -*- coding:utf-8 -*-
import calendar
import os
import datetime
import sqlite3
from tkinter import Tk, Toplevel, Frame, Button, Canvas, Text, END
from tkinter.ttk import Progressbar, Style

from calendar4wiz import Calendar
from config import Config
from sqlite import DB
from controls import Controls
from load_data import wiz_week_index, read_data


class WeekeryApp(Tk):
    def __init__(self):
        super().__init__()

        self.canvas_show = 'frequency'  # or 'sleep'

        # +++++++++++++++
        # +  GUI_setup  +
        # +++++++++++++++
        self.title('Weekery')
        Style().theme_use('vista')
        '''
        root
        |- Progressbar.bottom
        |- Frame_Left
        |  |- Frame_btn_left.top
        |  |  |- left(btn{d,w,m,y})
        |  |  |- right(btn{+,-})
        |  |  |- Frame_btn_mid
        |  |     |- <.left
        |  |     |- >.right
        |  |     |- calendar.middle
        |  |- Canvas_up.top
        |  |- Canvas_down.top
        |- Frame_Right
           |- Frame_btn_right
           |  |- btn_setting.right
           |  |- btn_reload.right
           |  |- btn_switch.left
           |- Text.bottom.top expand=both
        '''
        # ====== Frames ======
        self.frame_left = Frame(self)

        self.frame_right = Frame(self)

        self.frame_btn_left = Frame(self.frame_left)
        self.frame_btn_left.config(bg='white')
        self.frame_btn_mid = Frame(self.frame_btn_left)

        self.frame_btn_right = Frame(self.frame_right)
        self.frame_btn_right.config(bg='white')

        # ====== Buttons ======
        self.btn_days = Button(self.frame_btn_left, text='日', command=self.days)
        self.btn_days.config(bg='white')
        self.btn_weeks = Button(self.frame_btn_left, text='周', command=self.weeks)
        self.btn_weeks.config(bg='white')
        self.btn_months = Button(self.frame_btn_left, text='月', command=self.months)
        self.btn_months.config(bg='white')
        self.btn_years = Button(self.frame_btn_left, text='年', command=self.years)
        self.btn_years.config(bg='white')
        self.btn_plus = Button(self.frame_btn_left, text='十', command=self.plus)
        self.btn_plus.config(bg='white')
        self.btn_minus = Button(self.frame_btn_left, text='一', command=self.minus)
        self.btn_minus.config(bg='white')
        self.btn_switch = Button(self.frame_btn_left, text='睡眠|词频')
        self.btn_switch.config(bg='white')

        self.btn_previous = Button(self.frame_btn_mid, text='《', command=self.previous)
        self.btn_previous.config(bg='white')
        self.btn_backward = Button(self.frame_btn_mid, text='》', command=self.backward)
        self.btn_backward.config(bg='white')
        self.btn_calendar = Button(self.frame_btn_mid, text="日历", command=self.ask_selected_date)
        self.btn_calendar.config(bg='white')

        self.btn_reload = Button(self.frame_btn_right, text='重载')
        self.btn_reload.config(bg='white')
        self.btn_settings = Button(self.frame_btn_right, text='设置')
        self.btn_settings.config(bg='white')

        # ====== Others ======
        self.canvas_up = Canvas(self.frame_left)
        self.canvas_up.config(width=800, height=300, bg='white', bd=1)
        self.canvas_up.config(highlightthickness=0)
        self.canvas_down = Canvas(self.frame_left)
        self.canvas_down.config(width=800, height=300, bg='white', bd=1)
        self.canvas_down.config(highlightthickness=0)

        self.pgb = Progressbar(self, orient='horizontal', length=1000, mode='determinate')

        self.notes = Text(self.frame_right, width=50)
        self.notes.config(bg='azure')
        self.notes.insert(END, 'Weekery Notes models still in developing')

        # ====== Packing ======
        # level-1
        self.pgb.pack(side='bottom', fill='both')

        # level-1
        self.frame_left.pack(side='left', fill='both', expand='YES')
        # # level-2
        self.frame_btn_left.pack(side='top', fill='both')
        self.canvas_down.pack(side='top', fill='both', expand='YES')
        self.canvas_up.pack(side='top', fill='both', expand='YES')
        # # # level-3
        self.btn_days.pack(side='left')
        self.btn_weeks.pack(side='left')
        self.btn_months.pack(side='left')
        self.btn_years.pack(side='left')
        self.btn_switch.pack(side='right')
        self.btn_minus.pack(side='right')
        self.btn_plus.pack(side='right')
        self.frame_btn_mid.pack(side='top')
        # # # # level-4
        self.btn_previous.pack(side='left')
        self.btn_backward.pack(side='right')
        self.btn_calendar.pack(side='top')

        # level-1
        self.frame_right.pack(side='left', fill='both', expand='YES')
        # # level-2
        self.frame_btn_right.pack(side='top', fill='both')
        # # # level-3
        self.btn_settings.pack(side='right')
        self.btn_reload.pack(side='right')
        # # level-2
        self.notes.pack(side='top', fill='both', expand='YES')

        # ++++++++++++++++++
        # +  Import class  +
        # ++++++++++++++++++
        self.cfg = Config()
        db_path = self.cfg.cache_dir + '/weekery.db'
        self.conn = sqlite3.connect(db_path)

        id_filenames, id_dates = wiz_week_index(self.cfg)

        if self.cfg.last_read == 20160000:
            read_data(self, self.cfg, self.pgb, id_dates, id_filenames, 'all')
        else:
            read_data(self, self.cfg, self.pgb, id_dates, id_filenames)

        self.controls = Controls(self.conn)

        self.conn.commit()

    def ask_selected_date(self):
        select_calendar = CalendarPopup()
        self.wait_window(select_calendar)
        print(select_calendar.selected_days)

        return select_calendar.selected_days

    def days(self):
        pass

    def weeks(self):
        pass

    def months(self):
        pass

    def years(self):
        pass

    def previous(self):
        pass

    def backward(self):
        pass

    def plus(self):
        pass

    def minus(self):
        pass


class CalendarPopup(Toplevel):
    def __init__(self):
        self.selected_days = None
        super().__init__()
        self.title('选择日期')

        self.frame_cal = Frame(self)

        self.calendar = Calendar(self.frame_cal, firstweekday=calendar.MONDAY)
        self.btn_select = Button(self.frame_cal, text="Select", command=self.select_focus_days)

        self.btn_select.pack(side="bottom")
        self.calendar.pack(expand=1, fill='both')

        self.frame_cal.pack()

    def select_focus_days(self):
        back = Calendar.selection(self.calendar)
        if back:
            self.selected_days = back.strftime('%Y%m%d')
        self.destroy()


if __name__ == '__main__':
    app = WeekeryApp()
    app.mainloop()
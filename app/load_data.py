# -*- coding: utf-8 -*-
import os
import datetime
import sqlite3
import logging
import operator
import wiz_core as wc
from collections import Counter
from config import Config
from sqlite import DB
from tkinter import Tk
from tkinter.messagebox import showinfo, showwarning
from tkinter.ttk import Progressbar


def wiz_week_index(cfg):
    """ get index of wiz files, include filename format check
    :param cfg: Config() from outer space
    :return:
        id_filenames: a list to store the week file path
            [type] list.str
            [e.g.] ['2017/17[11.27-12.03]W48.ziw', '2017/17[12.04-12.10]W49.ziw', '2017/17[12.11-12.17]W50.ziw']
        id_dates: a list to store this week int index
            [type] list.tuple
            [e.g.] [(20171127, 20171203), (20171204, 20171210)]
    """
    wiz_path_folder = cfg.work_dir
    folder_contents = os.listdir(wiz_path_folder)
    # [type] list.str
    # [e.g.] ['2017', '2018', 'wizfolder.ini']
    id_filenames = []
    id_dates = []
    for year_folder in folder_contents:
        wiz_path_folder_comb = os.path.join(wiz_path_folder, year_folder)
        if os.path.isfile(wiz_path_folder_comb):
            continue
        
        try:
            int(year_folder)
        except ValueError:  # year_folder is not a number string, int(year_folder) raise error
            showwarning("警告", '"年份文件夹:[' + year_folder + ']应当为年份数字如2018，已忽略，如需导入请修改格式"')
            continue
        
        year_folder_contents = os.listdir(wiz_path_folder_comb)
        for file_name in year_folder_contents:
            # judge whether record correct
            year = r'20' + file_name[0:2] + '.'
            day_op = file_name[3:8]
            day_ed = file_name[9:14]
            try:
                op = datetime.datetime.strptime(year + day_op, '%Y.%m.%d')
                ed = datetime.datetime.strptime(year + day_ed, '%Y.%m.%d')
                id_filenames.append(year_folder + '\\' + file_name)
                id_dates.append((int(op.strftime('%Y%m%d')), int(ed.strftime('%Y%m%d'))))
            except ValueError:
                showwarning("警告", '周记文件:[' + file_name + ']格式错误,请修改为形如18[01.01-01.07]W01的格式')
                continue
    return id_filenames, id_dates


def read_one_file(cfg, days, year_file_name):
    """read the given weekery wiz file, store table DAYS into [database.db]
    :param cfg: Config() from outer space
    :param days: days = DB('DAYS')
    :param year_file_name: file name to read
        [type] str
        [e.g.] '2017/17[11.27-12.03]W48.ziw'
    :return notes: string to store week notes
        [type] str
    """
    work_dir = cfg.work_dir
    file_path = os.path.join(work_dir, year_file_name)
    
    # judge whether record correct
    year_folder, file_name = os.path.split(year_file_name)
    year = r'20' + file_name[0:2] + '.'
    day_op = file_name[3:8]
    day_ed = file_name[9:14]
    try:
        op = datetime.datetime.strptime(year + day_op, '%Y.%m.%d')
        ed = datetime.datetime.strptime(year + day_ed, '%Y.%m.%d')
    except ValueError:
        showwarning("警告", '周记文件:[' + file_name + ']格式错误,请修改为形如18[01.01-01.07]W01的格式')
        return
    
    # read wiz file
    soup_list, _ = wc.read_ziw(file_path)
    df_list = wc.table2dataframe(soup_list[0], cfg.color_kind)
    notes = wc.read_notes(soup_list[0])
    
    # remove first row 'table head' and first column 'time head'
    string_data = df_list[0][0].drop(0, axis=1).drop(0, axis=0)   # df_list[0][0] is the df.string in first[0] table
    kind_data = df_list[0][1].drop(0, axis=1).drop(0, axis=0)    # df_list[0][1] is the df.kind in first[0] table
    
    # columns number not equal to title date range
    if ed - op != datetime.timedelta(string_data.shape[1] - 1):
        showwarning("警告", '周记文件:[' + file_name + ']中,表格中的天数与标题时间段的天数不符, 请修改文件名后重新加载')
        return
    
    # generate date range list.int
    date_generated = [int((op + datetime.timedelta(days=x)).strftime('%Y%m%d')) for x in range(0, (ed-op).days + 1)]
    
    # ========== data dealing =============
    def group(L):  # [1,2,3, 5,6] -> [(1,3), (5,6)]
        first = last = L[0]
        for l in L[1:]:
            if n - 0.5 == last:   # Part of the group, bump the end
                last = l
            else:   # Not part of the group, yield current group and start a new
                yield first, last
                first = last = l
        yield first, last   # Yield the last group

    # set removed time_range
    for n, date in enumerate(date_generated):
        # skip columns all NaN
        if kind_data.count().iloc[n] == 0:
            continue
        
        # day_record = [ID,fun,rest,work,compel,useless,sleep, frequency]
        # [e.g.] [20170120, 5, 6, 3, 2, 1, 5, "{'a':1, 'b':2, 'c':3}"]
        record = [date, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, '{}']
        cfg.last_read = date
        # --------- count kind_time -----------
        one_day_kind = kind_data.iloc[:, n]
        kind_num = one_day_kind.value_counts() * 0.5
        for i, kind in enumerate(['fun', 'rest', 'work', 'compel', 'useless', 'sleep']):
            if kind in kind_num.index:
                record[i+1] = kind_num[kind]   # skip ID which is [0] in record
        
        # --------- count frequency -----------
        one_day_string = string_data.iloc[:, n]
        string_num = one_day_string.value_counts().to_dict()
        # split '|' by itmes, e.g. A|B|C in records, eash item A, B, C count for 0.33 unit
        for key in list(string_num.keys()):
            s = key.split('|')
            devide = len(s)
            if devide > 1:
                for ss in s:
                    if ss in string_num.keys():
                        string_num[ss] += round(string_num[key] / devide, 2)
                    else:
                        string_num[ss] = round(string_num[key] / devide, 2)         
                string_num.pop(key, None)
        # split '+' by items
        for key in list(string_num.keys()):
            s = key.split('+')
            if len(s) > 1:
                for ss in s:
                    if ss in string_num.keys():
                        string_num[ss] += string_num[key]
                    else:
                        string_num[ss] = string_num[key]
                string_num.pop(key, None)
        # remove ":" in the key
        for key in list(string_num.keys()):
            pop_judge = 0
            if ':' in key:
                s = key.split(':')[0]
                pop_judge += 1
            if '：' in key:
                s = key.split('：')[0]
                pop_judge += 1
                
            if pop_judge:
                if pop_judge >= 2:
                    showwarning("警告", "既有'：'又有':'，您这是闹哪样？这样会报错的，哼！")
                if s in string_num.keys():
                    string_num[s] += string_num[key]
                else:
                    string_num[s] = string_num[key]
                string_num.pop(key)
            else:
                pass
            
        # sort the result
        sorted_string = sorted(string_num.items(), key=operator.itemgetter(1), reverse=True)
        string_num = dict(sorted_string)
        
        record[-1] = str(string_num)
        # >>> write into [database.db]
        days.add(tuple(record), 'ID, fun, rest, work, compel, useless, sleep, frequency')
        
        # ------------- count sleep range --------------
        sl_kd = list(map(int, one_day_kind[one_day_kind == 'sleep'].index))
        kd_nan = list(map(int, one_day_string[one_day_string.isnull()].index))
        sleep_val = [(val - 1) / 2 for val in sl_kd if val in kd_nan]
        sleep_morning = [val for val in sleep_val if val <= 12]
        sleep_afternoon = [val for val in sleep_val if val > 12]
        
        # judge whether sleep among noon
        over_noon = False
        if len(sleep_val) > 0:
            for period in group(sleep_val):
                if period == (0, 0):
                    pass
                if (period[0] < 12) and (12 < period[-1]):
                    # print('睡到午休')
                    over_noon = True
                    sleep_ed_today = period[-1]
                    # sleep over noon, the end of this period should belongs to today not tomorrow
                    if sleep_ed_today == 23.5:
                        # Except sleep from (11:00, 24:00) to tomorrow
                        pass
                    else:
                        # ![Note]! the time is the index of a half hour
                        #          so the sleep_ed +0.5 is the real end of sleep end
                        days.add((date_generated[n], sleep_ed_today + 0.5), 'ID, sleep_ed')
        else:
            # probably no sleep result in that day, l = []
            pass

        # vectorization sleep time
        if sleep_morning:
            sleep_m = list(group(sleep_morning))
        else:
            # print('通宵')
            sleep_m = []
        if sleep_afternoon:
            sleep_a = list(group(sleep_afternoon))
        else:
            # print('熬夜')
            sleep_a = []
        
        # ++++++++++ deal with the time before 12:00 p.m. +++++++++++++
        if sleep_m:   # not stay up whole night
            if sleep_m[0][0] != 0:  # 0:00 still awake, but sleep before noon
                # overwrite today's sleep_st record
                days.add((date_generated[n], sleep_m[0][0]), 'ID, sleep_st')
            else:  # 0:00 fall asleep, not sure condition of yesterday
                # if yesterday did not record today's sleep_st, the sleep time is 0:00
                sleep_st_select = days.select('ID, sleep_st', (date, date))
                if (sleep_st_select[-1][-1] is None) and (not over_noon):
                    # today's do not have sleep_st record
                    days.add((date_generated[n], sleep_m[0][0]), 'ID, sleep_st')
            # not sleep overnoon, record today's sleep_ed
            if not over_noon:   
                # ![Note]! the time is the index of a half hour
                #          so the sleep_ed +0.5 is the real end of sleep end
                days.add((date_generated[n], sleep_m[-1][-1]+0.5), 'ID, sleep_ed')
            else:
                pass   # overnoon condition is recorded in former codes
        else:  # stay up whole night
            pass   # keep none records in [database.db]
        
        # ++++++++++ deal with the time after 12:00 p.m. +++++++++++++
        # change next days' record
        if sleep_a and sleep_a[-1][-1] == 23.5:  # sleep to next day
            # >>> write [database.db]
            next_day = datetime.datetime.strptime(str(date), '%Y%m%d') + datetime.timedelta(days=1)
            days.add((int(next_day.strftime('%Y%m%d')), sleep_a[-1][0] - 24), 'ID, sleep_st')
        else:
            pass   # including overnoon e.g.[(12.00, 13:00)], still not sleep at night
            # [12.00,24:00]
    
    cfg.update_config()
    # deliver [Notes] for TABLE Weeks' note column
    logging.info('Wiz weekery note [' + file_name + '] has been successfully loaded.')
    return notes

    
def read_data(root, cfg, pgb, id_dates, id_filenames, order="default", dialog=True):
    last_date = cfg.last_read
    today = int(datetime.datetime.today().strftime('%Y%m%d'))

    db_path = cfg.cache_dir + '/weekery.db'

    conn = sqlite3.connect(db_path)
    days = DB(conn, 'DAYS')
    weeks = DB(conn, 'WEEKS')
    months = DB(conn, 'MONTHS')
    years = DB(conn, 'YEARS')
    
    read_list = []
    date_list = []
    
    if order == "default":
        for id_date, id_filename in zip(id_dates, id_filenames):
            if (last_date <= id_date[-1]) and (today >= id_date[0]):
                read_list.append(id_filename)
                date_list.append(id_date)
        if not read_list:
            showinfo('通知', '暂无自上次运行时间到今日可读周记, 请新建本周周记后再次运行！')
            return

    if isinstance(order, int):
        start_date = int((datetime.datetime.today() - datetime.timedelta(weeks=order)).strftime('%Y%m%d'))
        for id_date, id_filename in zip(id_dates, id_filenames):
            if (start_date <= id_date[-1]) and (today >= id_date[0]):
                read_list.append(id_filename)
                date_list.append(id_date)
        if not read_list:
            showinfo('通知', '暂无' + str(order) +'周前到今日可读周记, 请新建对应周记后再次运行！')
            return
        
    if order == "all":
        days.drop_table()
        weeks.drop_table()
        months.drop_table()
        years.drop_table()
        for id_date, id_filename in zip(id_dates, id_filenames):
            if today >= id_date[0]:
                read_list.append(id_filename)
                date_list.append(id_date)
        if not read_list:
            showinfo('通知', '暂无到今日为止的可读周记，请新建本周周记后再次运行！')
            return
        
    if not read_list:
        return
    # ++++++++++++++++++++++
    # + Start summary mode +
    # ++++++++++++++++++++++
    notes_list = []
    pgb['maximum'] = len(read_list)
    for i, week_file in enumerate(read_list):
        # TABLE DAYS filled in this function
        notes_list.append(read_one_file(cfg, days, week_file))
        # update progressbar
        pgb['value'] = i
        root.update()
    
    # =========== Weeks summary  ===============
    for i, note in enumerate(notes_list):
        # calculate the weed_id (middle of week)
        st_weekery = date_list[i][0]
        week_mid = datetime.datetime.strptime(str(st_weekery), '%Y%m%d') + datetime.timedelta(days=3)
        week_id = int(week_mid.strftime('%Y%m%d'))   # id for TABLE WEEKS index
        
        # standardize week start day (Mon) and end day(Mon)
        week_st = week_mid - datetime.timedelta(days=week_mid.weekday())
        week_ed = week_st + datetime.timedelta(days=6)
        week_st_id = int(week_st.strftime('%Y%m%d'))
        week_ed_id = int(week_ed.strftime('%Y%m%d'))
        
        queries = days.select('ID, fun, rest, work, compel, useless, sleep, frequency, sleep_st, sleep_ed', (week_st_id, week_ed_id))
        if queries:
            record = _meanimize(queries, week_id)
            record.append(str(note))
            weeks.add(tuple(record))
        else:
            continue
        
    # ============= Months summary ================
    month_st = datetime.datetime.strptime(str(date_list[0][0]), '%Y%m%d')
    month_ed = datetime.datetime.today()
    month_set = set()
    for i in range((month_ed - month_st).days):
        month_set.add((month_st + datetime.timedelta(i)).strftime("%Y%m"))

    month_rk = sorted(month_set)
    for month_str in month_rk:
        month_id = int(month_str + '15')
        month_st_id = int(month_str + '00')
        month_ed_id = int(month_str + '32')
        
        queries = days.select('ID, fun, rest, work, compel, useless, sleep, frequency, sleep_st, sleep_ed', (month_st_id, month_ed_id))
        if queries:
            record = _meanimize(queries, month_id)
            months.add(tuple(record))
        else:
            continue
        
    # ============= Years summary ==================
    year_st = int(str(date_list[0][0])[:4])
    year_ed = int(datetime.datetime.today().strftime('%Y%m%d')[:4])
    
    if year_st != year_ed:
        year_rk = [y for y in range(year_st, year_ed+1) if year_st != year_ed]
    else:
        year_rk = [year_st]
    
    for year_int in year_rk:
        year_id = year_int * 10000 + 601
        year_st_id = int(str(year_int)+'0000')
        year_ed_id = int(str(year_int)+'1232')
        
        queries = months.select('ID, fun, rest, work, compel, useless, sleep, frequency, sleep_st, sleep_ed', (year_st_id, year_ed_id))
        if queries:
            record = _meanimize(queries, year_id)
            years.add(tuple(record))
        else:
            continue
        
    pgb['value'] = len(read_list)
    conn.commit()
    conn.close()
    
    if dialog:
        showinfo('初始化：第5步(共5步)', '周记文件读取完成！')


def _meanimize(query_results, target_id):
    """
    [input] query_results: must in this format
    >> models.select('ID, fun, rest, work, compel, useless, sleep, frequency, sleep_st, sleep_ed')
    """
    funs = [q[1] for q in query_results if q[1] is not None]
    rests = [q[2] for q in query_results if q[2] is not None]
    works = [q[3] for q in query_results if q[3] is not None]
    compels = [q[4] for q in query_results if q[4] is not None]
    uselesses = [q[5] for q in query_results if q[5] is not None]
    sleeps = [q[6] for q in query_results if q[6] is not None]
    frequencies = [Counter(eval(q[7])) for q in query_results if q[7]]
    sleep_sts = [q[8] for q in query_results if q[8] is not None]
    sleep_eds = [q[9] for q in query_results if q[9] is not None]
    
    frequency = Counter({})
    for f in frequencies:
        frequency += f
    frequen = dict(frequency.most_common(15))
    total = sum(frequency.values())
    frequen['Others'] = total - sum(frequen.values())
    
    fun = round(sum(funs) / len(funs), 1)
    rest = round(sum(rests) / len(rests), 1)
    work = round(sum(works) / len(works), 1)
    compel = round(sum(compels) / len(compels), 1)
    useless = round(sum(uselesses) / len(uselesses), 1)
    sleep = round(sum(sleeps) / len(sleeps), 1)
    sleep_st = round(sum(sleep_sts) / len(sleep_sts), 1) if len(sleep_sts) > 0 else 0
    sleep_ed = round(sum(sleep_eds) / len(sleep_eds), 1) if len(sleep_eds) > 0 else 0
    
    record = [target_id, fun, rest, work, compel, useless, sleep, sleep_st, sleep_ed, str(frequen)]
    
    return record
        

if __name__ == '__main__':
    Root = Tk()
    Root.title('WizStatistics')
    Root.config(bg='white')
    
    Cfg = Config(Root)
    Pgb = Progressbar(Root, orient='horizontal', length=500, mode='determinate')
    Pgb.pack()

    ID_FileNames, ID_Dates = wiz_week_index(Cfg)
    read_data(Root, Cfg, Pgb, ID_Dates, ID_FileNames, 'all', dialog=True)
    Root.mainloop()
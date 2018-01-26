# -*- coding: utf-8 -*-
import os
import datetime
import wiz_core as wc
from config import Config
from tkinter import Tk
from tkinter.messagebox import showinfo, showwarning, askyesno


def wiz_week_index():
    """ get index of wiz files, include filename format check
    :param wiz_path_folder: read from config.txt directly
        [type] str
        [e.g.] '/Time Log/My Weekry'
    :return:
        id_filenames: a list to store the week file path
            [type] list.str
            [e.g.] ['2017/17[11.27-12.03]W48.ziw', '2017/17[12.04-12.10]W49.ziw', '2017/17[12.11-12.17]W50.ziw']
    """
    wiz_path_folder = Config().work_dir
    folder_contents = os.listdir(wiz_path_folder)
    # [type] list.str
    # [e.g.] ['2017', '2018', 'wizfolder.ini']
    id_filenames = []
    for year_folder in folder_contents:
        wiz_path_folder_comb = os.path.join(wiz_path_folder, year_folder)
        if os.path.isfile(wiz_path_folder_comb):
            continue
        
        try:
            int(year_folder)
        except ValueError:  # year_folder is not a number string, int(year_folder) raise error
            showwarning("警告",'"年份文件夹:[' + year_folder + ']应当为年份数字如2018，已忽略，如需导入请修改格式"')
            continue
        
        year_folder_contents = os.listdir(wiz_path_folder_comb)
        for file_name in year_folder_contents:
                id_filenames.append(os.path.join(year_folder, file_name))
            
    return id_filenames


def read_one_file(year_file_name):
    """read the given weekery wiz file, store table DAYS into [datebase.db]
    :param year_file_name: file name to read
        [type] str
        [e.g.] '2017/17[11.27-12.03]W48.ziw'
    """
    work_dir = Config().work_dir
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
    df_list = wc.table2dataframe(soup_list[0], Config().color_kind)
    notes = wc.read_notes(soup_list[0])
    
    # remove first row 'table head' and first column 'time head'
    string_data = df_list[0][0].drop(0, axis=1).drop(0, axis=0)   # df_list[0][0] is the df.string in first[0] table
    kind_data = df_list[0][1].drop(0, axis=1).drop(0, axis=0)    # df_list[0][1] is the df.kind in first[0] table
    
    # columns number not equal to title date range
    if ed - op != datetime.timedelta(string_data.shape[1] - 1):
        showwarning("警告", '周记文件:[' + file_name + ']中,表格中的天数与标题时间段的天数不符, 请修改文件名')
        return
    
    # generage date range list.int
    date_generated = [int((op + datetime.timedelta(days=x)).strftime('%Y%m%d')) \
                      for x in range(0, (ed-op).days + 1)]
    
    # ========== data dealing =============
    ## set removed time_range
    for n, date in enumerate(date_generated):
        # day_record = [ID,fun,rest,work,compel,useless,sleep,sleep_st,sleep_ed,frequency]
        # [e.g.] [20170120, 5, 6, 3, 2, 1, 5, -1.5, 6.0, "{'a':1, 'b':2, 'c':3}"]
        record = [date, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, '']
        # skip columns all NaN
        if kind_data.count().iloc[n] == 0:
            continue
        
        # count kind_time
        one_day_kind = kind_data.iloc[:, n]
        kind_num = one_day_kind.value_counts() * 0.5
        for i, kind in enumerate(['fun','rest','work','compel','useless','sleep']):
            if kind in kind_num.index:
                record[i+1] = kind_num[kind]   # skip ID which is [0] in record
        print(record)
        
        # count frequency
        one_day_string = string_data.iloc[:, n]
        string_num = one_day_string.value_counts().to_dict()
        print(string_num)
        
        # count sleep range
        l = one_day_kind[one_day_kind == 'sleep'].index
        result = list(map(int, l))
        print(result)
        break
    
    # ========= write table DAYS of [database.db] ==========
    # to be continued

    
def read_data():
    pass

if __name__ == '__main__':
    root = Tk()
    root.title('ImageDBH')
    root.config(bg='white')
    id_filenames = wiz_week_index()
    read_one_file(id_filenames[-2])
    root.mainloop()
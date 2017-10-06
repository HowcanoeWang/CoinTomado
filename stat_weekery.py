# -*- coding: utf-8 -*-
import os
import pandas as pd
import matplotlib.pyplot as plt
from wiz_core import read_ziw, table2dataframe


def folder_path():
    # default path
    wiz_path = os.path.expanduser(r'~/Documents/My Knowledge/Data/')
    user_email = '18251920822@126.com'
    folder = r'/Time Log/My Weekry/2017'
    dir_combine = wiz_path + user_email + folder

    if not os.path.exists(dir_combine):
        print('[Warning]: Default wiz_note folder not applicable, trying load custom folder.')
        # try to load custom config file
        if not os.path.exists('config.txt'):
            print('[Warning]: Custom config file "config.txt" not exist.')
            with open('config.txt', 'w+') as f:
                f.write("wiz_path = r'" + wiz_path + "'")
                f.write("\nuser_email = r'" + user_email + "'")
                f.write("\nfolder = r'" + folder + "'")
            print('[Info]: Custom config file "config.txt" has been created\n'
                  '[Info]: Please edit it and run this program again.')
            input('[KeyInput]: Press <Enter> to quit')
            quit()
        # custom config file exist
        else:
            f =  open('config.txt')
            for line in f.read().split('\n'):
                _locals = locals()
                wiz_path = _locals['wiz_path']
                user_email = _locals['user_email']
                exec(line, globals(), _locals)
                folder = _locals['folder']
            f.close()
            dir_combine = wiz_path + user_email + folder

            if not os.path.exists(dir_combine):
                print('[Warning]: Could not find the following wiz_note folder:\n' + dir_combine)
                print('[Warning]: Please reedit it again and then run this program.')
                input('[KeyInput]: Press <Enter> to exit')
                quit()

    return dir_combine


def reload_kind_data(wiz_path_folder):
    # simple dataframe using data from color_kind
    # date    |sleep|fun|rest|work|compel|useless|
    # 2017/9/1|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
    # 2017/9/2|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
    kind_time_total = pd.DataFrame(columns=['fun', 'rest', 'work',
                                            'compel', 'useless', 'sleep'])

    # read all tables in folder '2017'
    soup_list, file_list = read_ziw(wiz_path_folder)
    for soup, file in zip(soup_list, file_list):
        df_list = table2dataframe(soup, color_kind)
        # remove first row 'table head' and first column 'time head'
        data = df_list[0][1].drop(0, axis=1).drop(0, axis=0)
        # get time_range
        year = r'20' + file[0:2] + '.'
        day_op = file[3:8]
        day_ed = file[9:14]
        dates = pd.date_range(year + day_op, year + day_ed)
        # set container
        kind_time = pd.DataFrame(columns=['fun', 'rest', 'work',
                                          'compel', 'useless', 'sleep'])
        # set removed time_range
        rm = []
        for n, _ in enumerate(dates):
            if data.count().iloc[n] - data.shape[0] != 0:
                # skip columns all NaN
                rm.append(n)
                continue
            one_day = data.iloc[:, n]
            num = one_day.value_counts() * 0.5
            kind_time = kind_time.append(num)
        dates = dates.delete(rm)
        kind_time.index = dates
        kind_time_total = kind_time_total.append(kind_time)
    kind_time_total = kind_time_total.fillna(0)
    kind_time_total.to_pickle('kind_time_total.pkl')

    return kind_time_total

def kind_plot(kind_time_total):
    # =============== Data preparation ===================
    # group data by month
    kind_time_month = kind_time_total.resample('M').mean().fillna(0)
    kind_time_month.index = kind_time_month.index.to_period('M')

    # group data by week
    kind_time_week = kind_time_total.resample('W').mean().dropna(axis=0, how='all')
    kind_time_week.index = kind_time_week.index.week

    # =============== Plot preparation ===================
    plt.style.use('ggplot')
    fig, axs = plt.subplots(2, 1)

    # --------------- Month plot ---------------------
    ax1 = kind_time_month.plot(kind='bar', title='Year View (Month.mean)', ax=axs[0], legend=False)
    ax1.set_ylabel('Hours')
    ax1.set_xlabel('Month')
    ax1.xaxis.grid()
    ax1.set_xticklabels(kind_time_month.index, rotation=0)
    # shrink current axis by 13%
    #box1 = ax1.get_position()
    #ax1.set_position([box1.x0, box1.y0, box1.width * 1.13, box1.height])
    #ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax1.legend(loc='best', ncol=2)

    # --------------- Week plot ------------------
    ax2 = kind_time_week.plot(kind='bar', title='Year View (Week.mean)', ax=axs[1], legend=False)
    ax2.set_xlabel('Week No.')
    ax2.set_ylabel('Hours')
    ax2.xaxis.grid()
    ax2.set_xticklabels(kind_time_week.index, rotation=0)

    fig.set_size_inches((10,7))
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # custom color kind
    color_kind = {"rgb(182, 202, 255)":"NaN",
                  "rgb(172, 243, 254)":"fun",       # 尽情娱乐
                  "rgb(178, 255, 161)":"rest",      # 休息放松
                  "rgb(254, 244, 156)":"work",      # 火力全开
                  "rgb(254, 207, 156)":"compel",    # 强迫工作
                  "rgb(247, 182, 255)":"useless",   # 无效工作
                  "rgb(238, 238, 238)":"sleep"}     # 睡眠时间

    # get folder path
    dir_combine = folder_path()

    # using cached results or reload latest data
    loop1 = True
    while loop1:
        reload = input("[KeyInput]: Using cached data or reload latest data? (c/r):")
        if reload == 'c':
            if os.path.exists('kind_time_total.pkl'):
                kind_time_total = pd.read_pickle('kind_time_total.pkl')
            else:
                print('[Warning]: Cached data not exist, reload data from wiz notes')
                kind_time_total = reload_kind_data(dir_combine)
            loop1 = False
        elif reload == 'r':
            kind_time_total = reload_kind_data(dir_combine)
            loop1 = False
        else:
            print('[Warning]: Please input only "c" or "r"')

    # draw picture interface
    loop2 = True
    while loop2:
        Route1 = input('[KeyInput]: Show summary? (y/n):')
        if Route1 == 'y':
            kind_plot(kind_time_total)
            loop2 = False
        elif Route1 == 'n':
            print('[Warning]: In developing')
        else:
            print('[Warning]: Please input only "n" or "y"')

    # input('[KeyInput]: Press <Enter> to quit')
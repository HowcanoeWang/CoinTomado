# -*- coding: utf-8 -*-
import os
import sys
import wiz_core
import datetime
import pandas as pd
import matplotlib.pyplot as plt


def read_year_folder(wiz_path_folder_comb):
    # simple dataframe using data from color_kind
    # date    |sleep|fun|rest|work|compel|useless|
    # 2017/9/1|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
    # 2017/9/2|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
    kind_time_folder = pd.DataFrame(columns=['fun', 'rest', 'work',
                                             'compel', 'useless', 'sleep'])
    soup_list, file_list = wiz_core.read_ziw(wiz_path_folder_comb)

    for soup, file in zip(soup_list, file_list):
        df_list = wiz_core.table2dataframe(soup, color_kind)

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
            if data.count().iloc[n] == 0:
                # skip columns all NaN
                rm.append(n)
                continue
            one_day = data.iloc[:, n]
            num = one_day.value_counts() * 0.5
            kind_time = kind_time.append(num)

        dates = dates.delete(rm)
        kind_time.index = dates
        kind_time_folder = kind_time_folder.append(kind_time)

    return kind_time_folder


def reload_kind_data(wiz_path_folder):
    kt_total = pd.DataFrame(columns=['fun', 'rest', 'work',
                                            'compel', 'useless', 'sleep'])
    folder_contents = os.listdir(wiz_path_folder)

    for year_folder in folder_contents:
        wiz_path_folder_comb = os.path.join(wiz_path_folder, year_folder)
        if os.path.isfile(wiz_path_folder_comb):
            continue
        else:
            # read year folder one by one
            kt_folder = read_year_folder(wiz_path_folder_comb)
            kt_total = kt_total.append(kt_folder)

    kt_total = kt_total.fillna(0)
    kt_total.to_pickle('kind_time_total.pkl')

    return kt_total


def kind_plot(df_month, df_week):
    # =============== Plot preparation ===================
    plt.style.use('ggplot')
    fig, axs = plt.subplots(2, 1)

    # --------------- Month plot ---------------------
    ax1 = df_month.plot(kind='bar', title='Year View (Month.mean)', ax=axs[0], legend=False)
    ax1.set_ylabel('Hours')
    ax1.set_xlabel('Month')
    ax1.xaxis.grid()
    ax1.set_xticklabels(df_month.index, rotation=0)
    ax1.legend(loc='best', ncol=2)

    # --------------- Week plot ------------------
    ax2 = df_week.plot(kind='bar', title='Year View (Week.mean)', ax=axs[1], legend=False)
    ax2.set_xlabel('Week No.')
    ax2.set_ylabel('Hours')
    ax2.xaxis.grid()
    ax2.set_xticklabels(df_week.index, rotation=0)

    fig.set_size_inches((10, 7))
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # custom color kind
    color_kind = {"rgb(182, 202, 255)": "NaN",
                  "rgb(172, 243, 254)": "fun",       # 尽情娱乐
                  "rgb(178, 255, 161)": "rest",      # 休息放松
                  "rgb(254, 244, 156)": "work",      # 火力全开
                  "rgb(254, 207, 156)": "compel",    # 强迫工作
                  "rgb(247, 182, 255)": "useless",   # 无效工作
                  "rgb(238, 238, 238)": "sleep"}     # 睡眠时间
    kind_time_total = pd.DataFrame(columns=['fun', 'rest', 'work',
                                            'compel', 'useless', 'sleep'])
    # get folder path
    wiz_dir = wiz_core.load_config('weekery_folder')

    # =========== using cached results or reload latest data ===========
    loop1 = True
    loop2 = True
    while loop1:
        reload = input("[Input  ]: Using cached data or reload latest data? (c/r):")
        if reload == 'c':
            if os.path.exists('kind_time_total.pkl'):
                kind_time_total = pd.read_pickle('kind_time_total.pkl')
            else:
                print('[Warning]: Cached data not exist, reload data from wiz notes')
                kind_time_total = reload_kind_data(wiz_dir)
            loop1 = False
        elif reload == 'r':
            kind_time_total = reload_kind_data(wiz_dir)
            loop1 = False
        else:

            print('[Warning]: Please input only "c" or "r"')

    # =========== draw picture interface ================
    # == Default show ==
    year_now = str(datetime.datetime.now().year)
    y_st = year_now + '-01-01'
    y_ed = year_now + '-12-31'
    # select current year
    kind_time_year2show = kind_time_total.loc[y_st:y_ed]
    try:
        # group data by month
        kind_time_month = kind_time_year2show.resample('M').mean().fillna(0)
        kind_time_month.index = kind_time_month.index.to_period('M')
        # group data by week
        kind_time_week = kind_time_year2show.resample('W').mean().dropna(axis=0, how='all')
        kind_time_week.index = kind_time_week.index.week
        # plot show
        kind_plot(kind_time_month, kind_time_week.iloc[-10:])
    except TypeError:
        print('[Warning]: No data obtained. Please check your "Config.txt" or wiz folder')
        input('[Input  ]: Press <enter> to exit')
        loop2 = False

    # ^Default show^
    # |- "n" -> Adjust mode
    # |   |- Year Adjust Mode
    # |   |   |- Input year directly
    # |   |   |- "q" -> back to upper stage
    # |   |- Week Adjust Mode
    # |   |   |- "<" -> go backward
    # |   |   |- ">" -> go forward
    # |   |   |- "q" -> back to upper stage
    # |- "q" -> Quit

    while loop2:
        route1 = input('[Input  ]: Adjust time period? (y/q):')
        if route1 == 'y':
            loop2 = False
            loop3 = True
    # == Adjust Mode ==
        # === Year Adjust ===
            while loop3:
                year_list = [x for x in os.listdir(wiz_dir) if '.' not in x]
                route_y = input('[Info   ]: Set year (' + str(year_list)[1:-1] + ", 'q'):")
                if route_y in year_list:
                    y_st = route_y + '-01-01'
                    y_ed = route_y + '-12-31'
                    w_st = -10
                    w_ed = 0
                    kind_time_year2show = kind_time_total.loc[y_st:y_ed]
                    if kind_time_year2show.empty:
                        print('[Warning]: No data in that year!')
                    else:
                        # input current year -> go to week change
                        if route_y != str(datetime.datetime.now().year):
                            # group data by month
                            kind_time_month = kind_time_year2show.resample('M').mean().fillna(0)
                            kind_time_month.index = kind_time_month.index.to_period('M')
                            # group data by week
                            kind_time_week = kind_time_year2show.resample('W').mean().dropna(axis=0, how='all')
                            kind_time_week.index = kind_time_week.index.week
                            # plot show
                            kind_plot(kind_time_month, kind_time_week.iloc[-10:])

        # === Week Adjust Mode ===
                        loop4 = True
                        w_len = len(kind_time_week)
                        if w_len <= 10:   # data length to small to adjust, Mode Off
                            loop4 = False
                            kind_plot(kind_time_month, kind_time_week)
                        while loop4:
                            route2 = input('[Input  ]: "<" to forward; ">" to backward (</>/q):')
                            if route2 == '<':
                                if abs(w_st - 5) <= w_len:   # can go forward
                                    w_st -= 5
                                    w_ed -= 5
                                else:
                                    step = w_st + w_len
                                    w_st -= step
                                    w_ed -= step
                                    print("[Warning]: Can't go forward anymore")
                                kind_plot(kind_time_month, kind_time_week.iloc[w_st:w_ed])
                            elif route2 == '>':
                                if w_ed + 5 < 0:   # can go backward
                                    w_st += 5
                                    w_ed += 5
                                    kind_plot(kind_time_month, kind_time_week.iloc[w_st:w_ed])
                                else:
                                    step = 0 - w_ed
                                    w_st += step
                                    w_ed += step
                                    print("[Warning]: Can't go backward anymore")
                                    kind_plot(kind_time_month, kind_time_week.iloc[w_st:])
                            elif route2 == 'q':
                                loop4 = False
                            else:
                                print('[Warning]: Please input only "<" or ">" or "q"')
                elif route_y == 'q':
                    loop3 = False
                    loop2 = True
                else:
                    print('[Warning]: Please input only years in ' + str(year_list) + " or 'q'")

        elif route1 == 'q':
            loop2 = False
        else:
            print('[Warning]: Please input only "y" or "q"')

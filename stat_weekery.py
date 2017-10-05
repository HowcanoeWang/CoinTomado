# -*- coding: utf-8 -*-
import os
import pandas as pd
import matplotlib.pyplot as plt
from wiz_core import read_ziw, table2dataframe

wiz_path = r'C:\\Users\\' + os.getlogin() + r'\Documents\My Knowledge\Data\18251920822@126.com\\'
folder = r'Time Log\\My Weekry\\2017'

color_kind = {"rgb(182, 202, 255)":"NaN",
              "rgb(172, 243, 254)":"fun",       # 尽情娱乐
              "rgb(178, 255, 161)":"rest",      # 休息放松
              "rgb(254, 244, 156)":"work",      # 火力全开
              "rgb(254, 207, 156)":"compel",    # 强迫工作
              "rgb(247, 182, 255)":"useless",   # 无效工作
              "rgb(238, 238, 238)":"sleep"}     # 睡眠时间

# first, count different kind total time
# simple dataframe using data from color_kind
# date    |sleep|fun|rest|work|compel|useless|
# 2017/9/1|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
# 2017/9/2|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
kind_time_total = pd.DataFrame(columns=['fun', 'rest', 'work',
                                  'compel', 'useless', 'sleep'])

# read all tables in folder '2017'
soup_list, file_list = read_ziw(wiz_path + folder)
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
        num = one_day.value_counts()*0.5
        kind_time = kind_time.append(num)
    dates = dates.delete(rm)
    kind_time.index = dates
    kind_time_total = kind_time_total.append(kind_time)

kind_time_total = kind_time_total.fillna(0)



# group data by month
kind_time_month = kind_time_total.resample('M').mean().fillna(0)
kind_time_month.index=kind_time_month.index.to_period('M')

# group data by week
kind_time_week = kind_time_total.resample('W').mean().dropna(axis=0, how='all')
kind_time_week.index = kind_time_week.index.week

inloop = True
while inloop:
    Route1 = input('Show summary? (y/n)')
    if Route1 == 'y':
        plt.style.use('ggplot')
        ax1 = kind_time_month.plot(kind='bar', title='Year View (Month.mean)', figsize=(10, 4))
        ax1.set_ylabel('Hours')
        ax1.xaxis.grid()
        ax1.set_xticklabels(kind_time_month.index, rotation=0)
        # shrink current axis by 13
        box1 = ax1.get_position()
        ax1.set_position([box1.x0, box1.y0, box1.width * 1.13, box1.height])
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()

        ax2 = kind_time_week.plot(kind='bar', title='Year View (Week.mean)', figsize=(10, 4))
        ax2.set_xlabel('Week No.')
        ax2.set_ylabel('Hours')
        ax2.xaxis.grid()
        ax2.set_xticklabels(kind_time_week.index, rotation=0)
        # shrink current axis by 13%
        box2 = ax2.get_position()
        ax2.set_position([box2.x0, box2.y0, box2.width * 1.13, box2.height])
        ax2.legend(loc='center left',  bbox_to_anchor=(1, 0.5))
        plt.tight_layout()

        plt.show()
        input('Press <Enter> to quit')
        inloop = False
    elif Route1 == 'n':
        print('In developing')
    else:
        print('Please input only "n" or "y"')

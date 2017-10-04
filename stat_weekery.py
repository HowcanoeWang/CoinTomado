# -*- coding: utf-8 -*-
import os
import pandas as pd
from wiz_core import read_ziw, table2dataframe

wiz_path = r'C:\\Users\\' + os.getlogin() + r'\Documents\My Knowledge\Data\18251920822@126.com\\'
folder = r'Time Log\\My Weekry\\2017'

color_kind = {"rgb(182, 202, 255)":"NaN",
              "rgb(172, 243, 254)":"尽情娱乐",
              "rgb(178, 255, 161)":"休息放松",
              "rgb(254, 244, 156)":"火力全开",
              "rgb(254, 207, 156)":"强迫工作",
              "rgb(247, 182, 255)":"无效工作",
              "rgb(238, 238, 238)":"睡眠时间"}

# first, count different kind total time
# simple dataframe using data from color_kind
# date    |sleep|fun|rest|work|compel|useless|
# 2017/9/1|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
# 2017/9/2|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
kind_time = pd.DataFrame(columns=['fun', 'rest', 'work',
                                  'compel', 'useless', 'sleep'])

soup_list, file_list = read_ziw(wiz_path + folder)
for soup, file in zip(soup_list, file_list):
    df_list = table2dataframe(soup, color_kind)
    # remove first row 'table head' and first column 'time head'
    data = df_list[0][0].drop(0, axis=1).drop(0, axis=0)
    # get time_range
    year = r'20' + file[0:2] + '.'
    day_op = file[3:8]
    day_ed = file[9:14]
    dates = pd.date_range(year + day_op, year + day_ed)


    print(data)
    break



#for soup, file in zip(soup_list, file_list):
#    df_list = table2dataframe(soup, color_kind)
#    data = df_list[0][0]

#soup = soup_list[-1]
#df_list = table2dataframe(soup, color_kind)
#data = df_list[0][1]
#print(data)
#print(df_list[1])





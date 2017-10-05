# -*- coding: utf-8 -*-
import os
import pandas as pd
from wiz_core import read_ziw, table2dataframe

wiz_path = r'C:\\Users\\' + os.getlogin() + r'\Documents\My Knowledge\Data\18251920822@126.com\\'

folder_path = r'My Notes\\备份备忘\\'
file_name = r'健身记录.ziw'
file_path = wiz_path + folder_path + file_name
soup_list,_ = read_ziw(file_path)

df_list = table2dataframe(soup_list[0])
data = df_list[0][0]

data.columns = data.iloc[0]
data = data.drop(0, axis=0)


kind = data['项目']
number = data.drop(['参数', '日期', '项目'], axis=1).apply(pd.to_numeric, errors='coerce').sum(axis=1).astype(int)
number.index = kind
number.column = ['次数']
number = number.groupby(number.index).sum()

print(number)
input('Press <Enter> to exit')
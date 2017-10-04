# -*- coding: utf-8 -*-
import zipfile
import os
import numpy as np
import pandas as pd
import bs4
from bs4 import BeautifulSoup


def read_ziw(inputstr):
    file_list = []
    file_dir_list = []
    soup_list = []
    if os.path.isfile(inputstr):
        file_dir_list.append(inputstr)
    else:
        for name in os.listdir(inputstr):
            file_list.append(name[:-4])
            file_dir_list.append(inputstr + '\\' + name)
        
    for file_name in file_dir_list:
        zfile = zipfile.ZipFile(file_name, 'r')
        data = zfile.open('index.html')
        zfile.close()
        soup = BeautifulSoup(data.read(), "html5lib")
        soup_list.append(soup) 
        
    return soup_list, file_list


def table2dataframe(html, color_kind=None, header='off'):
    # if header == 'on':
    #     set first row as table header
    # if header == 'off':
    #     set number sequence as table header
    #
    # color_kind = {'rgb(0,0,0)':'black',
    #               'rgb(1,1,1)':'white', ...}
    #
    # df_list = [(df, kd), (df, kd),...]
    df_list = []
    tables = html.find_all('tbody')
    for table in tables:
        row = len(table)
        # count col number
        col_list = []
        for tr in table.children:
            len_tr = len(tr)
            # delete '\t' take over an empty column
            # for td in tr.children:
            #    if type(td) == bs4.element.NavigableString:
            #        len_tr -= 1
            col_list.append(len_tr)
        col = max(col_list)
        columns = np.arange(0, col)
        index = np.arange(0, row)
        # create empty DataFrame
        # df records string, kd records color
        df = pd.DataFrame(index=index, columns=columns)
        kd = pd.DataFrame(index=index, columns=columns)
        skip_index = np.zeros([row, col], dtype=np.bool)
        for r, tr in enumerate(table.children):
            #c = 0
            for c, td in enumerate(tr.children):
            #for td in tr.children:
                if type(td) == bs4.element.NavigableString:
                    continue
                else:
                    attrs = td.attrs
                if td.string == None:
                    for sr in td.children:
                        if sr.string:
                            string = str(sr.string)
                        else:
                            string = np.nan
                else:
                    string = td.string

                if 'rowspan' in attrs.keys():
                    rowspan = int(attrs['rowspan'])
                    #if rowspan == 1:
                    #    rowspan = False
                else:
                    rowspan = False
                if 'colspan' in attrs.keys():
                    colspan = int(attrs['colspan'])
                    #if colspan == 1:
                    #    rowspan = False
                else:
                    colspan = False
                if rowspan == colspan == 1:
                    rowspan = colspan = False

                if 'style' in attrs.keys():
                    style = attrs['style']
                else:
                    style = False
                # fresh skip_index
                if style:
                    if 'background-color: ' in style:
                        color_str = style.split('background-color: ')[-1][:-1]
                        if color_kind:
                            color = color_kind[color_str]
                        else:
                            color = color_str
                    else:
                        color = np.nan
                if rowspan:
                    for x in range(1, rowspan):
                        df.ix[r + x][c] = string
                        kd.ix[r + x][c] = color
                        skip_index[r + x][c] = True                      
                if colspan:
                    for x in range(1, colspan):
                        df.ix[r][c + x] = string
                        kd.ix[r][c + x] = color
                        skip_index[r][c + x] = True
                # input string into df according to skip_index
                # then c + 1 to check next cell
                # until next cell's skip_index == False
                # save current sting to that cell
                while skip_index[r][c]:
                    c += 1
                df.ix[r][c] = string
                kd.ix[r][c] = color
                # change skip_index to True if cell already has value
                skip_index[r, c] = True
                
        df_list.append([df, kd])
    return df_list
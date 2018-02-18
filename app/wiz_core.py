# -*- coding: utf-8 -*-
import re
import zipfile
import os
import numpy as np
import pandas as pd
import bs4
from bs4 import BeautifulSoup


def read_ziw(input_string):
    '''
    if input_string is file
    [output]
        soup_list = ['...']
        file_list = ['...']

    if input_string is folder
    [output]
        soup_list = ['', '', '', ...]
        file_list = ['', '', '', ...]

    '''
    file_list = []
    file_dir_list = []
    soup_list = []
    if os.path.isfile(input_string):
        file_dir_list.append(input_string)
    else:
        for name in os.listdir(input_string):
            file_list.append(name[:-4])
            file_dir_list.append(input_string + '\\' + name)

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
            for c, td in enumerate(tr.children):
                if type(td) == bs4.element.NavigableString:
                    continue
                else:
                    attrs = td.attrs

                if td.string == None:
                    string = ''
                    for item in td.contents:
                        if isinstance(item, bs4.element.NavigableString):
                            string += str(item)
                    if string == '':
                        string = np.nan
                else:
                    string = td.string

                if 'rowspan' in attrs.keys():
                    rowspan = int(attrs['rowspan'])
                    if rowspan == 1:
                        rowspan = False
                else:
                    rowspan = False

                if 'colspan' in attrs.keys():
                    colspan = int(attrs['colspan'])
                    if colspan == 1:
                        colspan = False
                else:
                    colspan = False

                if 'style' in attrs.keys():
                    style = attrs['style']
                else:
                    style = False

                # input string into df according to skip_index
                # then c + 1 to check next cell
                # until next cell's skip_index == False
                # save current sting to that cell
                while skip_index[r][c]:
                    c += 1
                # fresh skip_index
                if style:
                    if 'background-color:' in style:
                        color_soup = style.split('background-color:')[-1][:-1]
                        color_str = str(color_soup).lstrip()
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
                # fill in data
                df.ix[r][c] = string
                kd.ix[r][c] = color
                # change skip_index to True if cell already has value
                skip_index[r, c] = True

        df_list.append([df, kd])

    return df_list


def read_notes(html):
    h1 = html.h1
    tags = h1.next_siblings

    ''' # method 1 use string
    notes = h1.string
    for tag in tags:
        string = tag.string
        if isinstance(string, str):
            notes += tag.string
    '''

    # method 2 use dictionary
    string = re.sub('[:：]', ' ', h1.string.strip())
    notes = {string.split()[0]: string.split()[1]}
    for tag in tags:
        string = tag.string
        if isinstance(string, str):
            string = string.strip()
            key = re.search(r'(\[.+?\])|(【.*?】)', string)
            if key:
                key = key.group()
                tmp = key  # temp to save key
                value = string[len(key):]
            else:
                key = tmp
                value = string
            # save to dictionary
            if key not in notes:
                notes[key] = value
            else:
                notes[key] += value
    return notes

if __name__ == '__main__':
    file_path = r'C:\Users\Zero\Documents\My Knowledge\Data\zeroto521@gmil.com\My Weekery\2018\Exp.ziw'
    color_kind = {"rgb(182, 202, 255)": "NaN",
                  "rgb(172, 243, 254)": "fun",
                  "rgb(178, 255, 161)": "rest",
                  "rgb(254, 244, 156)": "work",
                  "rgb(254, 207, 156)": "compel",
                  "rgb(247, 182, 255)": "useless",
                  "rgb(238, 238, 238)": "sleep"}
    soup_list, _ = read_ziw(file_path)
    read_notes(soup_list[0])
    # df_list = table2dataframe(soup_list[0], color_kind)

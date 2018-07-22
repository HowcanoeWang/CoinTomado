# -*- coding: utf-8 -*-
import re
import zipfile
import os
import numpy as np
import pandas as pd
import bs4
from bs4 import BeautifulSoup
import pprint


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
        col_list = [len(tr.find_all('td')) for tr in table.children]
        '''
        delete '\t' take over an empty column
        >>> for td in tr.children:
        >>>     if type(td) == bs4.element.NavigableString:
        >>>         len_tr -= 1
        
        replaced by counting all <td> tag num to void '\t' problem
        >>> len(tr.find_all('td'))
        '''
        col = max(col_list)
        columns = np.arange(0, col)
        index = np.arange(0, row)
        # create empty DataFrame
        # df records string, kd records color
        df = pd.DataFrame(index=index, columns=columns)
        kd = pd.DataFrame(index=index, columns=columns)
        skip_index = np.zeros([row, col], dtype=np.bool)
        for r, tr in enumerate(table.children):
            for c, td in enumerate(tr.find_all('td')):
                if type(td) == bs4.element.NavigableString:
                    continue
                else:
                    attrs = td.attrs

                if td.string is None:
                    string = ''
                    for item in td.contents:
                        if isinstance(item, bs4.element.NavigableString):
                            string += str(item)
                        elif isinstance(item, bs4.element.Tag) and item.string is not None:
                            string += str(item.string)
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
    data = html.findAll(text=True)
    
    def visible(element):
        #print(str(element.parent.attrs))
        #print(element, '\n')
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', str(element.encode('utf-8'))):
            return False
        elif len(element.parent.attrs.keys()) > 0:
            if any(key in element.parent.attrs.keys() for key in ['rowspan','colspan']):
                return False
            elif 'style' in element.parent.attrs.keys():
                if any(keyword in dict(element.parent.attrs)['style'] for keyword in ['width:', 'background-color:']):
                    return False
        elif any(keyword in element for keyword in ['\t', '\n\n']):
            return False
        return True
    
    result = filter(visible, data)

    notes = {}
    _temp_key = ''
    _temp_value = ''
    _head = ''
    _text = ''
    for item in result:
        # the item is dict key
        print(_temp_key, notes.keys())
        if '【' in item and '】' in item:
            if _temp_key:
                notes[_temp_key] = _temp_value
            _temp_key = item
            _temp_value = ''
        # the item is not the key
        else:
            # this item is belonging to a key, append it to key.value
            if _temp_key: 
                _temp_value += item + '\n'
            else:
            # this item belongis to no key
            # often this happens in the head of notes
                if '总结' in item and not _head:
                    if ':' or '：' in item:
                        if len(item.split('：')) > 1:
                            ls = item.split('：')
                            notes[ls[0]] = ls[1]
                            _head = ls
                        elif len(item.split(':')) > 1:
                            ls = item.split(':')
                            notes[ls[0]] = ls[1]
                            _head = ls
                        else:
                            _text += item + '\n'
                    else:
                        _text += item + '\n'
                else:
                    _text += item + '\n'
                    
    notes['其他文字'] = _text
    return notes

if __name__ == '__main__':
    #file_path = r'D:\新建文件夹\18[05.28-06.03]W22.ziw'
    file_path = r'C:\Users\18251\Documents\My Knowledge\Data\18251920822@126.com\Time Log\My Weekry\2018\18[06.25-07.01]W26.ziw'
    color_kind = {"rgb(182, 202, 255)": "NaN",
                  "rgb(172, 243, 254)": "fun",
                  "rgb(178, 255, 161)": "rest",
                  "rgb(254, 244, 156)": "work",
                  "rgb(254, 207, 156)": "compel",
                  "rgb(247, 182, 255)": "useless",
                  "rgb(238, 238, 238)": "sleep"}
    soup_list, _ = read_ziw(file_path)
    notes = read_notes(soup_list[0])
    # df_list = table2dataframe(soup_list[0], color_kind)
    # print(df_list)
    print(notes)

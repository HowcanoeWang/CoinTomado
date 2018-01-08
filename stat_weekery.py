# -*- coding: utf-8 -*-
import os
import wiz_core
import datetime
import pandas as pd
import matplotlib.pyplot as plt


def wiz_week_index(wiz_path_folder):
    ''' get index of wiz files

    :param wiz_path_folder: read from config.txt directly
        [type] str
        [e.g.] '/Time Log/My Weekry'

    :return week_index: a dict to store the week number
        [type] dict.key.int;
               dict.list.int
        [e.g.] {2017: [48, 49, 50], 2018: []}
        
    :return week_filename: a dict to store the week
        [type] dict.key.int; dict.list.str
        [e.g.] {2017: ['17[11.27-12.03]W48.ziw', '17[12.04-12.10]W49.ziw', '17[12.11-12.17]W50.ziw'],
                2018: []}
    '''
    week_index = dict()
    week_filename = dict()

    folder_contents = os.listdir(wiz_path_folder)
    # [type] list.str
    # [e.g.] ['2017', '2018', 'wizfolder.ini']


    for year_folder in folder_contents:
        wiz_path_folder_comb = os.path.join(wiz_path_folder, year_folder)
        if os.path.isfile(wiz_path_folder_comb):
            continue
        else:
            try:
                year_folder_int = int(year_folder)
                year_folder_contents = os.listdir(wiz_path_folder_comb)
                week_list = []
                week_filename_list = []
                for file_name in year_folder_contents:
                    try:
                        week = int(file_name[-6:-4])
                        week_list.append(week)
                        week_filename_list.append(file_name)
                    except ValueError:
                        print('[Warning]:wiz file name [' + file_name + '] is not in correct format: \
                               YY[MM.DD-MM.DD]WNo. [e.g.]17[12.11-12.17]W50')

                week_index[year_folder_int] = week_list
                week_filename[year_folder_int] = week_filename_list
            except ValueError:   # year_folder is not a number string, int(year_folder) raise error
                print('[Warning]: "year_folder":[' + year_folder + '] should be a number')
                continue
            
    return week_index, week_filename


def read_one_file(file_path):
    ''' read the given weekery wiz file into a required format pd.DataFrame
    :param file_path: the path of wiz file to read
    :return df_string: DataFrame to store the time serious
        [type] pd.DataFrame
        [e.g.] date    |0:00 |0:30 |1:00 |...|23:00|23:30|
               2017/9/1| str | str | str |...| str | str |
               2017/9/2| str | str | str |...| str | str |
    :return df_kind: DataFrame to store the time kind
        [type] pd.DataFrame
        [e.g.] date    | 0:00  | 0:30  |1:00 |...|23:00|23:30|
               2017/9/1|useless|useless|sleep|...|sleep|sleep|
               2017/9/2|sleep  | sleep |sleep|...|sleep|sleep|
    :return week_notes:
        [type] dict.key.int; dict.list.str
        [e.g.] {2017: ['note_string1', 'note_string2', 'note_string3'],
                2018: []}
    # will be removed in the future
    :return kind_time: simple dataframe using data from color_kind
        [type] pd.DataFrame
        [e.g.] date    |sleep|fun|rest|work|compel|useless|
               2017/9/1|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
               2017/9/2|7.5  |3.5|4.5 |3.5 |0.5   |0.5    |
    :return sleep_time: simple dataframe to record sleep time
        [type] pd.DataFrame
        [e.g.] date    |start|send |total|
               2017/9/1|22:30|07:00|8.5  |
    '''
    # split path and file name
    _, file_name = os.path.split(file_path)
    # set container
    time_columns = ['00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30',
                    '04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30',
                    '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
                    '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
                    '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
                    '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30']
    df_kind = pd.DataFrame(columns=time_columns)
    df_string = pd.DataFrame(columns=time_columns)

    kind_time = pd.DataFrame(columns=['fun', 'rest', 'work',
                                      'compel', 'useless', 'sleep'])

    # soup_list have only one element because read_one_file
    # [e.g.] soup_list = [contents]
    soup_list, _ = wiz_core.read_ziw(file_path)

    df_list = wiz_core.table2dataframe(soup_list[0], color_kind)
    
    # remove first row 'table head' and first column 'time head'
    # df_list[0] is this wiz file first table
    # df_list[0][0] is the df.string in former table
    # df_list[0][1] is the df.kind in former table
    string_data = df_list[0][0].drop(0, axis=1).drop(0, axis=0)
    kind_data = df_list[0][1].drop(0, axis=1).drop(0, axis=0)

    # to be removed in the future
    data = kind_data

    # get time_range
    year = r'20' + file_name[0:2] + '.'
    day_op = file_name[3:8]
    day_ed = file_name[9:14]

    try:
        dates = pd.date_range(year + day_op, year + day_ed)
        # set removed time_range
        rm = []
        for n, _ in enumerate(dates):
            if data.count().iloc[n] == 0:
                # skip columns all NaN
                rm.append(n)
                continue

            # to be removed to other place in the future for hours count
            one_day = data.iloc[:, n]
            num = one_day.value_counts() * 0.5
            kind_time = kind_time.append(num)

            # insert here
            one_day_string = string_data.iloc[:, n]
            df_string = df_string.append(one_day_string)
            one_day_kind = kind_data.iloc[:, n]
            df_kind = df_kind.append(one_day_kind) # raise RuntimeWarning


        dates = dates.delete(rm)
        # to be removed in the future
        kind_time.index = dates

        # insert here
        df_string.index = dates
        df_kind.index = dates

    except ValueError:     # judge whether wiz.file title correct
        print('[Warning]: Wiz file name['+ file_name +'] invalid, please check wiz folder and rename it!')
                                                   
    return kind_time  #, df_string, df_kind

    
def read_recent_week(week_index, week_filename):
    ''' Judge the time of now, and read current week (it will change by time going)
    :param week_index: return of wiz_week_index()
        [type] dict.list
    :param week_filename: return of wiz_week_index()
        [type] dict.list

    :return kt_current_week: kind time current week
        [type] pd.DataFrame
    '''
    year_number = int(datetime.datetime.now().year)
    week_number = int(datetime.datetime.now().strftime("%W"))

    if year_number in week_index.keys():
        if week_number in week_index[year_number]:
            list_id = week_index[year_number].index(week_number)
            this_week_file_path = os.path.join(wiz_dir, str(year_number),
                                               week_filename[year_number][list_id])
            kt_current_week = read_one_file(this_week_file_path)
            if list_id - 1 >= 0:    # have previous week
                former_week_file_path = os.path.join(wiz_dir, str(year_number),
                                                     week_filename[year_number][list_id - 1])
                kt_former_week = read_one_file(former_week_file_path)
                kt_current_week = kt_current_week.append(kt_former_week)
            else:    # the first week of this year, load last year's last week
                if year_number -1 in week_index.keys():
                    former_week_file_path = os.path.join(wiz_dir, str(year_number - 1),
                                                         week_filename[year_number - 1][-1])
                    kt_former_week = read_one_file(former_week_file_path)
                    kt_current_week = kt_current_week.append(kt_former_week)
        else:
            print("[Warning]: Can not find current week's record, please add a new weekery note in [Wiz Note]")
            kt_current_week = pd.DataFrame(columns=['fun', 'rest', 'work','compel', 'useless', 'sleep'])
    else:
        print("[Warning]: Can not find current year's record, please add a new folder named current year in [Wiz Note]")
        kt_current_week = pd.DataFrame(columns=['fun', 'rest', 'work', 'compel', 'useless', 'sleep'])

    return kt_current_week


def read_former_weeks(week_index, week_filename):
    '''
    :param week_index:
    :param week_filename:
    :return:
    '''
    kt_former_weeks = pd.DataFrame(columns=['fun', 'rest', 'work', 'compel', 'useless', 'sleep'])
    year_number = int(datetime.datetime.now().year)
    week_number = int(datetime.datetime.now().strftime("%W"))

    for key in week_index.keys():
        if key < year_number:
            for week in week_index[key]:
                id = week_index[key].index(week)
                former_week_file_path = os.path.join(wiz_dir, str(key),
                                                     week_filename[key][id])
                kt_current_one_week = read_one_file(former_week_file_path)
                kt_former_weeks = kt_former_weeks.append(kt_current_one_week)
        elif key == year_number:
            for week in week_index[key]:
                if week < week_number:
                    id = week_index[key].index(week)
                    former_week_file_path = os.path.join(wiz_dir, str(key),
                                                         week_filename[key][id])
                    kt_current_one_week = read_one_file(former_week_file_path)
                    kt_former_weeks = kt_former_weeks.append(kt_current_one_week)
                else:
                    break
        else:
            break

    return kt_former_weeks


def merge_dataframe(df_old, df_new):
    '''
    :param df_old: the dataframe used as background
    :param df_new: the dataframe to cover old background

    :return df_latest: the merged dataframe

    :examples:
    # >>> import pandas as pd
    # >>> old = pd.DataFrame({'A': [1., 4., 7.], 'B': [2., 5., 9.], 'C': [3., 6., 8.]})
    # >>> old.index = ['12-2', '12-3', '12-4']
    # >>> old
    #       A	B	C
    # 12-2	1.0	2.0	3.0
    # 12-3	4.0	5.0	6.0
    # 12-4	7.0	9.0	8.0
    # >>> new = pd.DataFrame({'A': [1., 4.], 'B': [2., 5.], 'C': [3., 6.]})
    # >>> new.index = ['12-4', '12-5']
    # >>> new
    #       A	B	C
    # 12-4	1.0	2.0	3.0
    # 12-5	4.0	5.0	6.0
    # >>> latest = merge_dataframe(old, new)
    # >>> latest
    #       A	B	C
    # 12-2	1.0	2.0	3.0
    # 12-3	4.0	5.0	6.0
    # 12-4	1.0	2.0	3.0
    # 12-5	4.0	5.0	6.0
    '''
    for id in df_new.index:
        if id in df_old.index:
            df_old = df_old.drop(id)
    df_latest = pd.concat([df_old, df_new])

    return df_latest


def analyse(df_string, df_kind):
    '''
    :param df_string:
    :param df_kind:
    :return: dataframe for 'kind_plot'
    '''
    pass

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
        week_index, week_filename = wiz_week_index(wiz_dir)
        reload = input("[Input  ]: Load latest week's data (default) or refresh former data? (d/r):")
        if reload == 'd':
            # generate new version cached data
            if os.path.exists('kind_time_cache.pkl'):
                kt_former_data = pd.read_pickle('kind_time_cache.pkl')
                kt_current_week = read_recent_week(week_index, week_filename)
                kt_merge = merge_dataframe(kt_former_data,kt_current_week)
            else:
                print('[Warning]: Cached data not exist, reload data from wiz notes')
                kt_former_data = read_former_weeks(week_index, week_filename)
                kt_current_week = read_recent_week(week_index, week_filename)
                kt_merge = merge_dataframe(kt_former_data, kt_current_week)
            loop1 = False
        elif reload == 'r':
            kt_former_data = read_former_weeks(week_index, week_filename)
            kt_current_week = read_recent_week(week_index, week_filename)
            kt_merge = merge_dataframe(kt_former_data, kt_current_week)
            loop1 = False
        else:
            print('[Warning]: Please input only "d" or "r"')
            kt_merge= pd.DataFrame(columns=['fun', 'rest', 'work', 'compel', 'useless', 'sleep'])

        kind_time_total = kind_time_total.append(kt_merge)
        kind_time_total.to_pickle('kind_time_cache.pkl')

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
        #kind_time_week = kind_time_year2show.resample('W').mean().fillna(0)
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

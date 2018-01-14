import os, sys
import wiz_core
import datetime
import pandas as pd
import matplotlib.pyplot as plt


def wiz_week_index(wiz_path_folder):
    """ get index of wiz files
    :param wiz_path_folder: read from config.txt directly
        [type] str
        [e.g.] '/Time Log/My Weekry'
    :return:
        week_filenames: a list to store the week file path
            [type] list.str
            [e.g.] ['2017/17[11.27-12.03]W48.ziw', '2017/17[12.04-12.10]W49.ziw', '2017/17[12.11-12.17]W50.ziw']
    """

    folder_contents = os.listdir(wiz_path_folder)
    # [type] list.str
    # [e.g.] ['2017', '2018', 'wizfolder.ini']

    week_filenames = []
    for year_folder in folder_contents:
        wiz_path_folder_comb = os.path.join(wiz_path_folder, year_folder)
        if os.path.isfile(wiz_path_folder_comb):
            continue
        else:
            try:
                int(year_folder)
                year_folder_contents = os.listdir(wiz_path_folder_comb)
                for file_name in year_folder_contents:
                    week_filenames.append(os.path.join(year_folder, file_name))
            except ValueError:  # year_folder is not a number string, int(year_folder) raise error
                print('[Warning]: "year_folder":[' + year_folder + '] should be a number')
                continue

    return week_filenames


def read_one_file(file_path):
    """ read the given weekery wiz file into a required format pd.DataFrame
    :param file_path:
    :return:
        df_string: DataFrame to store the time serious
            [type] pd.DataFrame
            [e.g.] date    |0:00 |0:30 |1:00 |...|23:00|23:30|
                   2017/9/1| str | str | str |...| str | str |
                   2017/9/2| str | str | str |...| str | str |
        df_kind: DataFrame to store the time kind
            [type] pd.DataFrame
            [e.g.] date    | 0:00  | 0:30  |1:00 |...|23:00|23:30|
                   2017/9/1|useless|useless|sleep|...|sleep|sleep|
                   2017/9/2|sleep  | sleep |sleep|...|sleep|sleep|
        notes:
            [type] dict.key.int; dict.list.str
            [e.g.] {2017: ['note_string1', 'note_string2', 'note_string3'],
                    2018: []}
        sleep_time: simple dataframe to record sleep time
            [type] pd.DataFrame
            [e.g.] date    |start|send |total|
                   2017/9/1|22:30|07:00|8.5  |
    """
    # split path and file name
    _, file_name = os.path.split(file_path)

    notes = ''
    sleep_time = ''
    # set container
    df_kind = pd.DataFrame(columns=time_columns)
    df_string = pd.DataFrame(columns=time_columns)

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

    # get time_range
    year = r'20' + file_name[0:2] + '.'
    day_op = file_name[3:8]
    day_ed = file_name[9:14]


    try:
        dates = pd.date_range(year + day_op, year + day_ed)
        # set removed time_range
        rm = []
        for n, _ in enumerate(dates):
            if kind_data.count().iloc[n] == 0:
                # skip columns all NaN
                rm.append(n)
                continue

            one_day_string = string_data.iloc[:, n]
            one_day_string.index = time_columns
            df_string = df_string.append(one_day_string)
            one_day_kind = kind_data.iloc[:, n]
            one_day_kind.index = time_columns
            df_kind = df_kind.append(one_day_kind)  # raise RuntimeWarning

        dates = dates.delete(rm)

        df_string.index = dates
        df_kind.index = dates
    except ValueError:  # judge whether wiz.file title correct
        print('[Warning]: Wiz file name[' + file_name + '] invalid, please check wiz folder and rename it!')

    return df_string, df_kind, sleep_time, notes


def read_weeks(week_filenames, order="default"):
    if order == "default":
        read_list = week_filenames[-2:]
    elif order == "all":
        read_list = week_filenames
    else:
        read_list = None

    df_string_weeks = pd.DataFrame(columns=time_columns)
    df_kind_weeks = pd.DataFrame(columns=time_columns)
    sleep_time_weeks = ''
    notes_weeks = ''

    if read_list:
        length = len(read_list)
        for i, week_file in enumerate(read_list):
            print(str(round(i / length * 100, 2)) + r'%')
            week_file_path = os.path.join(wiz_dir, week_file)
            df_string, df_kind, sleep_time, notes = read_one_file(week_file_path)

            df_string_weeks = df_string_weeks.append(df_string)
            df_kind_weeks = df_kind_weeks.append(df_kind)

    return df_string_weeks, df_kind_weeks, sleep_time_weeks, notes_weeks


def merge_dataframe(df_old, df_new):
    """
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
    """
    for id in df_new.index:
        if id in df_old.index:
            df_old = df_old.drop(id)
    df_latest = pd.concat([df_old, df_new])

    return df_latest


def load_data(part_load=True):
    week_filenames = wiz_week_index(wiz_dir)
    if os.path.exists('weekery_database.xls') and part_load:
        db_string = pd.read_excel('weekery_database.xls', 'db_string')
        db_kind = pd.read_excel('weekery_database.xls', 'db_kind')

        db_string_new, db_kind_new, db_sleep_time_new, db_notes_new = read_weeks(week_filenames)

        db_string = merge_dataframe(db_string, db_string_new)
        db_kind = merge_dataframe(db_kind, db_kind_new)
        db_sleep_time = db_sleep_time_new
        db_notes = db_notes_new
    else:
        db_string, db_kind, db_sleep_time, db_notes = read_weeks(week_filenames, order="all")

    writer = pd.ExcelWriter('weekery_database.xls', engine='xlwt')
    db_string.to_excel(writer, 'db_string', engine='xlwt')
    db_kind.to_excel(writer, 'db_kind', engine='xlwt')
    writer.save()

    return db_string, db_kind, db_sleep_time, db_notes


if __name__ == "__main__":
    # custom color kind
    color_kind = {"rgb(182, 202, 255)": "NaN",
                  "rgb(172, 243, 254)": "fun",       # 尽情娱乐
                  "rgb(178, 255, 161)": "rest",      # 休息放松
                  "rgb(254, 244, 156)": "work",      # 火力全开
                  "rgb(254, 207, 156)": "compel",    # 强迫工作
                  "rgb(247, 182, 255)": "useless",   # 无效工作
                  "rgb(238, 238, 238)": "sleep"}     # 睡眠时间
    kind_columns = ['fun', 'rest', 'work', 'compel', 'useless', 'sleep']
    time_columns = ['00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30',
                    '04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30',
                    '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
                    '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
                    '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
                    '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30']

    # get folder path
    wiz_dir = wiz_core.load_config('weekery_folder')

    db_string, db_kind, _, _ = load_data()
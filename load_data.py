import os
from config import Config
from tkinter import Tk
from tkinter.messagebox import showinfo, showwarning, askyesno


def wiz_week_index(wiz_path_folder):
    """ get index of wiz files, include filename format check
    :param wiz_path_folder: read from config.txt directly
        [type] str
        [e.g.] '/Time Log/My Weekry'
    :return:
        id_filenames: a list to store the week file path
            [type] list.str
            [e.g.] ['2017/17[11.27-12.03]W48.ziw', '2017/17[12.04-12.10]W49.ziw', '2017/17[12.11-12.17]W50.ziw']
        id_dates: a list to store the date index
            [type] list.str
            [e.g.] [(20171127, 20171203), (20171204, 20171210), (20171211, 20171217)]
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

                    # 在这里增加文件格式检查代码

            except ValueError:  # year_folder is not a number string, int(year_folder) raise error
                showwarning("警告",'"年份文件夹":[' + year_folder + ']应当为年份数字如2018，已忽略，如需导入请修改格式。')
                continue
    id_filenames = []
    id_dates = []
    pass
    return id_filenames, id_dates

if __name__ == '__main__':
    root = Tk()
    root.title('ImageDBH')
    root.config(bg='white')
    work_dir = Config().work_dir
    id_filenames, id_dates = wiz_week_index(work_dir)
    root.mainloop()
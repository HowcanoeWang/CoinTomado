# -*- coding: utf-8 -*-
import os
import logging
import datetime
from configparser import ConfigParser, NoOptionError
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tkinter.simpledialog import askinteger
from tkinter.messagebox import showinfo, showwarning, askyesno


class Config(object):
    """
    path = .../*.txt
    dir = .../somefolder
    """
    language = 'zh_cn'
    wiz_dir = os.path.normpath(os.path.expanduser(r'~/Documents/My Knowledge'))
    cache_dir = os.path.join(os.path.abspath('.'), 'cache')
    config_path = os.path.join(cache_dir, 'config.ini')
    user_email = 'your_wiz_account_email@web.com'
    weekery_dir = r'/My Weekery'
    work_dir = ''
    last_read = 20160000
    color_kind = {"rgb(182, 202, 255)": "NaN",
                  "rgb(172, 243, 254)": "fun",
                  "rgb(178, 255, 161)": "rest",
                  "rgb(254, 244, 156)": "work",
                  "rgb(254, 207, 156)": "compel",
                  "rgb(247, 182, 255)": "useless",
                  "rgb(238, 238, 238)": "sleep",
                  "rgb(255, 199, 200)": "NaN"}

    def __init__(self, root):
        self.root = root
        # create cache folder
        mkdir = False
        '''
        if not os.path.exists('C:/ProgramData'):
            os.mkdir('C:/ProgramData')
            mkdir1 = True
            os.mkdir(self.cache_dir)
            mkdir2 = True
        else:
        '''
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
            mkdir = True

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=os.path.join(
                                self.cache_dir, 'weekery.log'),
                            filemode='a')
        logging.info('\n\n' + '=' * 5 +
                     datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '=' * 5)

        if mkdir:
            logging.info(self.cache_dir + ' not exist, created successfully')

        if not os.path.exists(self.config_path):
            self._initialize_config()
        else:
            self._read_config()

    def _initialize_config(self):
        """
        Just read >>> [Default] part codes for main frame
        """
    # >>> [Default] select wiz data folder and it is true WizNote data folder
        if os.path.exists(self.wiz_dir) and os.path.exists(self.wiz_dir + '/Wiz.log') and os.path.exists(self.wiz_dir + '/Data'):
            wiz_dir = self.wiz_dir
        # v[Exception 1] user change WizNote default data folder
        else:
            showinfo('初始化：第1步(共5步)',
                     '选择您为知笔记的本地数据存储路径\n详见为知笔记->设置v->选项->数据存储')
            wiz_dir = ''
            loop = True
            while loop:
                wiz_dir = askdirectory(initialdir=r'C:/')
                if not wiz_dir:
                    logging.warning('You do not select any folder!')
                    ans = askyesno('警告', '您没有选择文件夹,重新选择？')
                    if not ans:
                        logging.info('Gave up folder selection')
                        self.root.destroy()
                        loop = False
                else:
                    if os.path.exists(wiz_dir + '/Wiz.log') and os.path.exists(wiz_dir + '/Data'):
                        self.wiz_dir = wiz_dir
                        loop = False
                    elif not os.path.exists(wiz_dir + '/Data'):
                        showwarning('警告', '[Data]文件夹不存在')
                        logging.warning(
                            '[' + wiz_dir + '/Data]' + 'is not a wiz data folder')
                        self.root.destroy()
                        loop = False
                    else:
                        ans = askyesno('警告', '此文件夹非为知笔记数据文件夹, 重新选择？')
                        if not ans:
                            logging.info('Gave up reselect wiz data folder')
                            self.root.destroy()
                            loop = False
            else:
                return
        # ^[Exception 1] ends

    # >>> [Default] user select a correct WizNote folder, find User_email
        wiz_dir_data = wiz_dir + '/Data'
        dir_list = os.listdir(wiz_dir_data)
        emails_list = []
        for items in dir_list:
            if not os.path.isfile(os.path.join(wiz_dir, items)):
                emails_list.append(items)

    # >>> [Default] user just use one account (only one email folder in "Data" )
        if len(emails_list) == 1:
            self.user_email = emails_list[0]
        # v[Exception 3] user has multiple accounts, let them select Account
        elif emails_list != [] and len(emails_list) > 1:
            diag_str = {}
            for i, email in enumerate(emails_list):
                diag_str[i] = email
            loop = True
            # ensure them input a right number
            while loop:
                ans = askinteger('初始化：第2步(共5步)',
                                 '选择当前用户名序号：\n' + str(diag_str))
                if ans in diag_str.keys():
                    self.user_email = diag_str[ans]
                    loop = False
                else:
                    if ans:
                        showinfo('提示', '仅限以下选择\n' + str(list(diag_str.keys())))
                    else:
                        showwarning('警告', '用户取消选择，初始化停止')
                        self.root.destroy()
                        loop = False
            else:
                return
        # ^[Exception 3] ends
        # v[Exception 4] there are no email folder in "Data" folder
        else:
            showwarning('警告', '未找到存在的用户名，请登陆为知笔记同步后再次运行')
            self.root.destroy()
            return
        # ^[Exception 4] ends

    # >>> [Default] select weekry folder
        wiz_dir_data_email = os.path.join(wiz_dir_data, self.user_email)
        showinfo('初始化：第3步(共5步)', '选择您的[周记]文件夹')
        loop = True
        while loop:
            weekery = askdirectory(initialdir=wiz_dir_data_email)
            if weekery:
                # if user misselects year folder as Weekery
                font, last = os.path.split(weekery)
                try:
                    length = len(last)
                    if length == 4:
                        int(last)
                        weekery = font
                    else:
                        pass
                except ValueError:
                    pass

                norm_weekery = os.path.normpath(weekery)
                norm_wdde = os.path.normpath(wiz_dir_data_email)

                _, weekery_dir = norm_weekery.split(norm_wdde)

                self.weekery_dir = weekery_dir
                self.work_dir = norm_weekery

                loop = False
            else:  # cancel selection
                ans = askyesno('警告', '您没有选择文件夹,重新选择？')
                if not ans:
                    self.root.destroy()
                    return

        self._write_config()

    def _read_config(self):
        config = ConfigParser()
        config.read(self.config_path)

        # basic configs
        self.wiz_dir = config.get('main', 'wiz_dir')
        self.user_email = config.get('main', 'user_email')
        self.weekery_dir = config.get('main', 'weekery_dir')
        self.language = config.get('main', 'language')

        # extended configs
        extend = False
        try:
            self.last_read = config.getint('main', 'last_read')
        except NoOptionError:
            config.set('main', 'last_read', str(self.last_read))
            extend = True
        try:
            self.color_kind = eval(config.get('main', 'color_kind'))
        except NoOptionError:
            config.set('main', 'color_kind', str(self.color_kind))
            extend = True
        # refresh config
        if extend:
            with open(self.config_path, 'w') as f:
                config.write(f)

        work_dir = self.wiz_dir + '\\Data\\' + self.user_email + self.weekery_dir
        if os.path.exists(work_dir):
            self.work_dir = work_dir
        else:
            logging.info('[' + work_dir + '] not exist when _read_config')
            # find whether computer change lead to username change only
            ans = askyesno(
                '警告', '周记路径[' + work_dir + ']不存在，重新初始化(Y)或手动编辑配置文件(N)？')
            if not ans:  # reedit
                showinfo('提示', '周记配置文件config.ini路径：\n' + self.config_path)
                logging.info('user selected to modify config mannually')
                self.root.destroy()
                return
            else:
                logging.info(
                    'user selected to initialize config automatically')
                self._initialize_config()

    def _write_config(self):
        config = ConfigParser()
        config.read(self.config_path)
        config.add_section('main')
        config.set('main', 'wiz_dir', self.wiz_dir)
        config.set('main', 'user_email', self.user_email)
        config.set('main', 'weekery_dir', self.weekery_dir)
        config.set('main', 'language', self.language)
        config.set('main', 'last_read', str(self.last_read))
        config.set('main', 'color_kind', str(self.color_kind))

        with open(self.config_path, 'w') as f:
            config.write(f)

        logging.info('Custom config file "config.ini" has been created')
        showinfo('初始化：第4步(共5步)', '配置文件初始化完成, 即将加载周记文件！')

    def update_config(self):
        config = ConfigParser()
        config.read(self.config_path)
        config.set('main', 'wiz_dir', self.wiz_dir)
        config.set('main', 'user_email', self.user_email)
        config.set('main', 'weekery_dir', self.weekery_dir)
        config.set('main', 'language', self.language)
        config.set('main', 'last_read', str(self.last_read))
        config.set('main', 'color_kind', str(self.color_kind))

        with open(self.config_path, 'w+') as f:
            config.write(f)


if __name__ == '__main__':
    # load_config('weekery_folder')
    root = Tk()
    root.title('ImageDBH')
    root.config(bg='white')
    conf = Config(root)
    root.mainloop()

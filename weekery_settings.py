# -*- coding: utf-8 -*-
import os
import sys

'''
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='myapp.log',
                    filemode='w')
'''

def load_config(name_folder):
    # default path
    wiz_path = os.path.expanduser(r'~/Documents/My Knowledge/Data/')
    user_email = 'your_wiz_account_email@web.com'
    folder = {'weekery_folder': r'/My Weekery',
              'exercise_folder': r'/My Exercies'}
    config_version = r'v1.0'
    config_version_now = r'v1.0'
    dir_combine = wiz_path + user_email + folder[name_folder]

    if not os.path.exists('C:/ProgramData'):
        os.mkdir('C:/ProgramData')
        os.mkdir('C:/ProgramData/WizStatistics')
        config_dir = 'C:/ProgramData/WizStatistics'
    else:
        if not os.path.exists('C:/ProgramData/WizStatistics'):
            os.mkdir('C:/ProgramData/WizStatistics')
            config_dir = 'C:/ProgramData/WizStatistics'
        else:
            config_dir = 'C:/ProgramData/WizStatistics'

    config_path = os.path.join(config_dir, 'config.txt')
    if os.path.exists(config_path):    
        f = open(config_path)
        for line in f.read().split('\n'):
            _locals = locals()
            exec(line, globals(), _locals)
            wiz_path = _locals['wiz_path']
            user_email = _locals['user_email']
            folder = _locals['folder']
            config_version = _locals['config_version']
        f.close()

        if config_version != config_version_now:
            print('[Info   ]:Old version config file detected, pass')  
            '''
            folder_new = {'weekery_folder': r'/My Weekery',
                          'exercise_folder': r'/My Exercies'}
            folder = folder_new
            config_version = config_version_now
            os.remove(os.path.join(config_dir, 'config.txt'))
            with open(os.path.join(config_dir,'config.txt'), 'w+') as f:
                f.write("wiz_path = r'" + wiz_path + "'")
                f.write("\nuser_email = r'" + user_email + "'")
                f.write("\nfolder = " + str(folder))
                f.write("\nconfig_version = r'" + config_version + "'")
               print('[Info   ]:Custom config file "config.txt" has been updated')
            '''   
            dir_combine = wiz_path + user_email + folder[name_folder]
        else:
            dir_combine = wiz_path + user_email + folder[name_folder]

        if not os.path.exists(dir_combine):
            # find whether computer change lead to username change only
            behind = dir_combine.split('/Documents/')[-1]
            dir_combine = os.path.expanduser(r'~/Documents/' + behind)
            if not os.path.exists(dir_combine):
                print('[Warning]: Could not find the following wiz_note folder:[' + dir_combine + ']')
                print('[Warning]: Please reedit it again and then run this program.')
                input('[Input  ]: Press <Enter> to exit')
                sys.exit(0)
        
    else:    # config.txt not exist
        print('[Info   ]:Custom config file "config.txt" not exist, created')
        with open(config_path, 'w+') as f:
            f.write("wiz_path = r'" + wiz_path + "'")
            f.write("\nuser_email = r'" + user_email + "'")
            f.write("\nfolder = " + str(folder))
            f.write("\nconfig_version = r'" + config_version_now + "'")
        print('[Info   ]:Custom config file "config.txt" has been created')
        print('[Info   ]:Please edit it and run this program again.')
        input('[Input  ]: Press <Enter> to quit')
        sys.exit(0)
    
    return dir_combine

if __name__ == '__main__':
    load_config('weekery_folder')

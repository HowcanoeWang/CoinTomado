# pip install pywin32
# pip install uiautomation
# pip install psutil
# https://stackoverflow.com/questions/10266281/obtain-active-window-using-python
import time
import psutil
import uiautomation as automation
import win32process
import win32gui

def chromeUrl(c, d):
    a = isinstance(c, automation.EditControl)
    b = "Address and search bar" in c.Name

while True:
    current = win32gui.GetForegroundWindow()
    text = win32gui.GetWindowText(current)
    threadid, pid = win32process.GetWindowThreadProcessId(current)
    try:
        p = psutil.Process(pid)
        p_name = p.name()
    except:
        continue

    sysout = f'{p_name}   |   {text}'
    if p_name == 'chrome.exe':
        # maybe look for Chrome history is an option
        '''
        control = automation.GetFocusedControl()
        controlList = []
        while control:
            controlList.insert(0, control)
            control = control.GetParentControl()
        if len(controlList) == 1:
            control = controlList[0]
        else:
            control = controlList[1]
        address_control = automation.FindControl(control, lambda c, d: isinstance(c, automation.EditControl) and "Address and search bar" in c.Name)
        print(address_control.CurrentValue())
        '''
        pass
        

    print(sysout)

    time.sleep(1)
## 数据库结构

### 时间金币表

#### Coin

| id   | date     | time_block | behavior__id | remark__id | kind_id | rowspan |
| ---- | -------- | ---------- | ------------ | ---------- | ------- | ------- |
| INT  | INT      | INT        | INT          | INT        | INT     | INT     |
| 0    | 20190101 | 1          | 2            | 2          | 0       | 1       |
| 1    | 20190101 | 1          | 1            | 1          | 0       | 3       |

> If happens at the same time, using the same TimeBlock
>
> | TimeBlock | TimeSt | TimeEd |
> | --------- | ------ | ------ |
> | 0         | 0：00  | 0：15  |
> | 1         | 0：16  | 0：30  |

#### Behavior

| id   | name      |
| ---- | --------- |
| INT  | CHAR(128) |
| 0    | 晚饭      |
| 1    | B站       |

#### Remark

| id   | name        |
| ---- | ----------- |
| INT  | CHAR（128） |
| 0    | 炒饭        |
| 1    | 看番        |

#### Kind

| id   | name      | color                |
| ---- | --------- | -------------------- |
| INT  | CHAR(128) | CHAR(32)             |
| 0    | 休闲娱乐  | RGB(255,255,255,190) |
| 1    | 高效工作  | RGB(255,255,0,190)   |

#### Color

| id   | name    | red  | green | blue | alpha |
| ---- | ------- | ---- | ----- | ---- | ----- |
| INT  | CHAR(8) | INT  | INT   | INT  | INT   |
| 0    | 红      | 255  | 0     | 0    | 0     |

#### Summary

| id   | date     | type | contents（.md） |
| ---- | -------- | ---- | --------------- |
| INT  | INT      | INT  | CHAR(512)       |
| 0    | 20170812 | 0    | # 每日总结\n    |
| 1    | 20170831 | 1    | # 月终总结\n    |
| 2    | 20170630 | 2    | # 季度总结\n    |

> 每月最后一天，每日总结变为月终总结，每季最后一天，月终总结变为季度总结

------

### 当前屏幕表

#### ScreenRecord

| id   | time                | device_id | app_id | app_title_id |
| ---- | ------------------- | --------- | ------ | ------------ |
| INT  | YYYY-MM-DD HH:MM:SS | INT       | INT    | INT          |
| 0    | 2017-08-09 10:00:01 | 0         | 1      | 1            |
| 1    | 2017-08-09 10:00:16 | 0         | 2      | 2            |

> 采样密度：15s

#### Device

| id   | Name           |
| ---- | -------------- |
| INT  | CHAR(64)       |
| 0    | 'NERV'         |
| 1    | 'NERV_SURFACE' |
| 2    | 'Pixel_XL2'    |

#### App

| id   | name                        | work_white_list |
| ---- | --------------------------- | --------------- |
| INT  | CHAR(64)                    | BOOL            |
| 0    | python  getCurrentWindow.py | TRUE            |
| 1    | Drawboard PDF               | TRUE            |

> 获取windows当前安装软件列表，https://www.cnblogs.com/dcb3688/p/4468770.html
>
> 如果软件不在白名单上，开启番茄钟的时候，会弹出专注的菜单

#### AppTitle

| id   | name                                                         |
| ---- | ------------------------------------------------------------ |
| INT  | CHAR(128)                                                    |
| 0    | C:\WINDOWS\System32\cmd.exe - python                         |
| 1    | Clark 等。 - 2000 - A review of past research on dendrometers.pdf |

在时间每天填写时间块的时候，旁边会辅助出现该时间块内的应用使用情况，以便进行决定

------

### Todo表

#### Project

| id   | name      | kind_id | task_id | comments  |
| ---- | --------- | ------- | ------- | --------- |
| INT  | CHAR(128) | INT     | INT     | CHAR(128) |
| 0    | 工作      | 1       | 0       | None      |
| 1    | 游戏      | 0       | 1       | 1         |

#### Task

| id   | name       | subtask_id | status | urgent | deadline   | pred_num | comments  |
| ---- | ---------- | ---------- | ------ | ------ | ---------- | -------- | --------- |
| INT  | CHAR(128)  | INT        | BOOL   | INT    | YYYY-MM-DD | INT      | CHAR(128) |
| 0    | 完成论文   | 0          | TRUE   | 1      | 2018-12-01 | 23       | None      |
| 1    | 女神异闻录 | None       | FALSE  | 4      | None       | 13       | None      |

> Status： TRUE=todo，FALSE=finished  
> Urgent： 0=默认，1=紧急且重要，2=紧急但不重要，3=重要但不紧急，4=不重要也不紧急    
> Deadline：None=someday

#### Subtask

| id   | name       | status |
| ---- | ---------- | ------ |
| INT  | CHAR(128)  | BOOL   |
| 0    | 完成第一章 | TRUE   |

### 番茄钟表

#### Tomatodo

| id   | task_id | subtask_id | st_time          | ed_time          | interrupted | reason    |
| ---- | ------- | ---------- | ---------------- | ---------------- | ----------- | --------- |
| INT  | INT     | INT        | TIME.MIN         | TIME.MIN         | BOOL        | CHAR(128) |
| 0    | 0       | 0          | 2017.09.19 12:03 | 2017.09.19 12:28 | FALSE       | None      |
| 1    | 1       | 1          | 2017.09.19 12:29 | 2017.09.19 12:34 | TRUE        | 上厕所    |

## 文件结构

待续
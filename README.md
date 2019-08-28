# CoinTomado（原WizStatistics）

集合艾力时间金币法、Todo列表，番茄钟于一体的时间管理软件

## 界面设计

待续

## 功能设计

1. 批量导入wiz（Extension， not in main app）
2. 自动检测电脑当前窗口
    1. 锁定检测：https://stackoverflow.com/questions/34514644/in-python-3-how-can-i-tell-if-windows-is-locked/43758104
    2. 为时间记录辅助参考
1. 每日评价颜色
2. 快捷键合并与标色
3. 睡眠统计
4. TodoList（自动计入时间块）
5. 番茄钟倒计时功能
6. 多端同步（服务器后台？）

## 数据库结构

### 时间金币表
#### Record

|id|date|block_id|Action_id|Remark_id|Kind_id|rowspan|
|---|---|---|---|---|---|---|
|INT|TIME.DAY|INT|INT|INT|INT|INT|
|0|2019/01/01|1|2|2|0|1|
|1|2019/01/01|1|1|1|0|3|
If happens at the same time, using the same block id

#### Block

| id   | Time_st  | Time_ed  |
| ---- | -------- | -------- |
| INT  | TIME.MIN | TIME.MIN |
| 0    | 0：00    | 0：15    |
| 1    | 0：16    | 0：30    |

#### Action

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

| id   | Name      | Color                |
| ---- | --------- | -------------------- |
| INT  | CHAR(128) | CHAR(32)             |
| 0    | 休闲娱乐  | RGB(255,255,255,190) |
| 1    | 高效工作  | RGB(255,255,0,190)   |

#### Summary

| id   | Time       | Type | Contents（md） |
| ---- | ---------- | ---- | -------------- |
| INT  | TIME.DAY   | INT  | CHAR(512)      |
| 0    | 2017.08.12 | 0    | # 每日总结\n   |
| 1    | 2017.08.31 | 1    | # 月终总结\n   |
| 2    | 2017.06.30 | 2    | # 季度总结\n   |

> 每月最后一天，每日总结变为月终总结，每季最后一天，月终总结变为季度总结

---

### 当前屏幕表
#### ScreenRecord
| id   | Time                | Devide_id | App_id | AppTitle_id |
| ---- | ------------------- | --------- | ------ | ----------- |
| INT  | TIME.DAY.MIN.SEC    | INT       | INT    | INT         |
| 0    | 2017.08.09 10:00:01 | 0         | 1      | 1           |
| 1    | 2017.08.09 10:00:16 | 0         | 2      | 2           |

> 采样密度：15s

#### Device

| id   | Name           |
| ---- | -------------- |
| INT  | CHAR(64)       |
| 0    | 'NERV'         |
| 1    | 'NERV_SURFACE' |
| 2    | 'Pixel_XL2'    |

#### App

| id   | Name                        | WorkWhiteList |
| ---- | --------------------------- | ------------- |
| INT  | CHAR(64)                    | BOOL          |
| 0    | python  getCurrentWindow.py | TRUE          |
| 1    | Drawboard PDF               | TRUE          |

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

---

### Todo表
#### Project

| id   | Name      | Kind_id | Task_id | Comments  |
| ---- | --------- | ------- | ------- | --------- |
| INT  | CHAR(128) | INT     | INT     | CHAR(128) |
| 0    | 工作      | 1       | 0       | None      |
| 1    | 游戏      | 0       | 1       | 1         |

#### Task

| id   | Name       | Subtask_id | Status | Urgent | Deadline   | PredNum | Comments  |
| ---- | ---------- | ---------- | ------ | ------ | ---------- | ------- | --------- |
| INT  | CHAR(128)  | INT        | BOOL   | INT    | TIME.DAY   | INT     | CHAR(128) |
| 0    | 完成论文   | 0          | TRUE   | 1      | 2018.12.01 | 23      | None      |
| 1    | 女神异闻录 | None       | FALSE  | 4      | None       | 13      | None      |

> Status： TRUE=todo，FALSE=finished  
> Urgent： 0=默认，1=紧急且重要，2=紧急但不重要，3=重要但不紧急，4=不重要也不紧急    
> Deadline：None=someday

#### Subtask

| id   | Name       | Status |
| ---- | ---------- | ------ |
| INT  | CHAR(128)  | BOOL   |
| 0    | 完成第一章 | TRUE   |

### 番茄钟表
#### Tomatodo

| id   | Task_id | Subtask_id | St_time          | Ed_time          | Interrupted | Reason    |
| ---- | ------- | ---------- | ---------------- | ---------------- | ----------- | --------- |
| INT  | INT     | INT        | TIME.MIN         | TIME.MIN         | BOOL        | CHAR(128) |
| 0    | 0       | 0          | 2017.09.19 12:03 | 2017.09.19 12:28 | FALSE       | None      |
| 1    | 1       | 1          | 2017.09.19 12:29 | 2017.09.19 12:34 | TRUE        | 上厕所    |

## 文件结构
待续
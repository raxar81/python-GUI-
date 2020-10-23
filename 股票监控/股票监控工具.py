# -*- coding: UTF-8 -*-

import tkinter
import tkinter as tk
from tkinter.ttk import *

import re
import time
import urllib3
import threading
import threadpool
import configparser
def treeviewClick(event):
    print ('双击')
    for item in tree.selection():
        item_text = tree.item(item,"values")
        print(item_text[0])#输出所选行的第一列的值
# treeview不显示颜色补丁方法
def fixed_map(option):
    return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]

# 停止监控
def stop_hit_me():
    global on_hit
    global b
    global b2
    on_hit = False

    # 点击停止监控，开始监控按钮变为可按状态，停止监控按钮为不可按状态
    b2['state'] = 'disabled'
    b['state'] = 'active'

# 开始监控
def hit_me():
    global on_hit
    global b
    global b2

    # 点击开始监控，开始监控按钮变为不可按状态，停止监控按钮为可按状态
    b['state']='disabled'
    b2['state']='active'
    on_hit = True

    # 开启线程后台循环更新数据
    timer = threading.Thread(target=getdata)
    timer.daemon = True
    timer.start()
    return

# 循环监控
def getdata():
    global tree
    global on_hit
    global timelable

    # 读取config.ini文件，读出需要监控的股票号
    cfg1 = "config.ini"
    conf = configparser.ConfigParser()
    conf.read(cfg1)
    numbers = conf.get("StockCode", "Code")

    # 当监控开关按下时，循环获取股票信息
    while(on_hit==True):
        # 待更新表格行数
        line=0

        # 清空表格
        x = tree.get_children()
        for item in x:
            tree.delete(item)

        # web请求获取股票信息
        http = urllib3.PoolManager(timeout=5.0)
        urllib3.disable_warnings()
        res = http.request('GET', 'http://hq.sinajs.cn/list=' + numbers)
        content = str(res.data, "gbk")
        numbersarray = content.split(";")
        numbersarray.pop()
        for one in numbersarray:
            pattern4 = re.compile(r'hq_str_([^=]*)', re.M)
            result114 = pattern4.findall(one)
            if result114:
                number = result114[0]
            pattern5 = re.compile(r'"([^"]*)"', re.M)
            result115 = pattern5.findall(one)
            if result115:
                allparts = result115[0].split(",")
                name = allparts[0]
                new = round(float(allparts[3]),2)
                percent = str(round((float(allparts[3]) - float(allparts[2])) / float(allparts[1]) * 100, 3))+"%"
                zhangdie = round(float(allparts[3]) - float(allparts[2]), 2)
            if zhangdie > 0:
                tree.insert("", line, values=(number, name, new, percent, zhangdie), tags=('redrow',))
            elif zhangdie < 0:
                tree.insert("", line, values=(number, name, new, percent, zhangdie), tags=('greenrow',))
            else:
                tree.insert("", line, values=(number, name, new, percent, zhangdie))
            timelable['text'] = '数据时间：'+allparts[30]+' '+allparts[31]
            line = line + 1
        time.sleep(3)

# 初始化窗口
window = tkinter.Tk()
# 窗口永远在windows最顶端
window.wm_attributes('-topmost',1)
# 程序标题
window.title("Rax 股票监控工具")
# 窗口大小
window.geometry('500x300')
# 是否可调整大小
window.resizable(0,0)

# 列表不显示颜色补丁
style = Style()
style.map("Treeview",foreground=fixed_map("foreground"),background=fixed_map("background"))

# 循环监控开关
on_hit = False

# 初始化显示更新时间的标签
timelable = tkinter.Label(window, text='', font=('Arial', 10))

# 标签放置位置
timelable.place(x=250, y=280, anchor='nw')

# 初始化数据表格
columns =("股票代码","股票名称","最新","涨幅","涨跌")
tree=Treeview(window, show = "headings", columns = columns,  selectmode = tk.BROWSE)

# 设置两种行颜色表示涨跌
tree.tag_configure('redrow', background='Salmon',foreground='black')
tree.tag_configure('greenrow', background='PaleGreen',foreground='black')
tree.pack()

# 设置每列数据的宽度
tree.column("股票代码",width=100)
tree.column("股票名称",width=100)
tree.column("最新",width=100)
tree.column("涨幅",width=100)
tree.column("涨跌",width=100)

# 设置表格头各列名称
tree.heading("股票代码",text="股票代码")
tree.heading("股票名称",text="股票名称")
tree.heading("最新",text="最新")
tree.heading("涨幅",text="涨幅")
tree.heading("涨跌",text="涨跌")

# 初始化开始监控按钮并设置位置
b = tkinter.Button(window, text='开始监控', font=('Arial', 10), width=10, command=hit_me)
b.place(x=150, y=230, anchor='nw')

# 初始化停止监控按钮并设置位置
b2 = tkinter.Button(window, text='停止监控', font=('Arial', 10), width=10, command=stop_hit_me)
b2.place(x=250, y=230, anchor='nw')

# 停止监控初始为不可点击状态
b2['state'] = 'disabled'

#加入双击显示详情功能
tree.bind('<Double-1>', treeviewClick)

# 启动程序
window.mainloop()

# -*- coding: UTF-8 -*-
# by sun
#use for tx cloud 用于下午推送第二天的课表
#此脚本仅2021年3月1日后可正常运行

import datetime
import time
import re
import requests
import json


def main_handler(event, context):

    global qqkey
    global mailuser
    global mailpwd
    global mailreceiver
    #QQ推送设置
    qqkey = '' #这里填Qmsg的KEY
    
            
    global db
    global weeknum
    global weekday

    # 读取课表数据字典
    with open('data.json', 'r') as f:
        db = json.load(f)
        f.close()

    #2021.3.1日后用realdatetime替换datatime

    realdatetime = datetime.datetime.now().strftime('%Y-%m-%d')
    datatime = "2021-05-11"
    a = time.strptime(str(datatime), "%Y-%m-%d")
    y = a.tm_year
    m = a.tm_mon
    d = a.tm_mday
    sj = Shijian(y,m,d)#实例化一个时间类用于获取日期处于第几周星期几
    weeknum = sj.get_weeknum()
    weekday = sj.get_weekday()

    if weekday == '0': #星期天提醒推送下周一的课程
        weeknum = weeknum+1
        weekday = 1
        cx = Cx(weeknum, weekday)  # 实例化一个查询类
        res1 = '今天的日期是：' + datatime + '\n' +'第%s周'%(weeknum-1) + '星期日' + '\n' + '今天没有课！' + '\n' + '明天的课程是ヾ(๑╹◡╹)ﾉ"'
        res2 = cx.get_dayclass()
        qqres = res1 + res2
        push = Push(qqres)#实例化推送类
        push.qqtext()
    elif weekday == '6':#星期六仅提醒今天是星期六
        qqres = '今天的日期是：' + datatime + '\n' + '第%s周' % weeknum + '星期六' + '\n' + '今天没有课！'
        push = Push(qqres)  # 实例化推送类
        push.qqtext()
    elif weekday == '5':#星期五推送提醒
        qqres = '今天的日期是：' + datatime + '\n' + '第%s周' % weeknum + '星期五' + '\n' + '周末愉快！'
        push = Push(qqres) # 实例化推送类
        push.qqtext()
    else:#星期一到星期四，推送第二天课程，仅QQ推送
        weeknum = weeknum
        weekday = weekday + 1
        cx = Cx(weeknum, weekday)  # 实例化一个查询类
        res1 = 'Hello，明天你有这些课哦٩(๑>◡<๑)۶ '
        res2 = cx.get_dayclass()
        qqres = res1 +res2
        push = Push(qqres) # 实例化推送类
        push.qqtext()


class Shijian: #时间处理类，获取日期是星期几及第几教学周

    def __init__(self,y,m,d):#初始化
        self.y = y
        self.m = m
        self.d = d

    def get_weeknum(self): #获取指定日期是第几教学周
        realweeknum = datetime.datetime(int(self.y), int(self.m), int(self.d)).isocalendar()[1]  # 一年中的第几周
        weeknum = realweeknum - 8
        return weeknum


    def get_weekday(self):#获取指定日期是星期几
        weekday = int(datetime.datetime(self.y,self.m,self.d).strftime("%w"))
        return weekday



class Cx: #查询类，查询当天及当周有哪些课程

    def __init__(self,weeknum,weekday):#初始化
        self.weeknum = weeknum
        self.weekday = weekday

    def parse(dayclass):#解析每天课程，将没课的节次替换为文本
        classlsit = []
        for i in range(6):
            if len(dayclass[i]) != 17:
                classlsit.append(dayclass[i])
            else:
                classlsit.append('没课！')
        return classlsit

    def get_dayclass(self):#获取每天的课程并返回课程结果
        weekclass_list = db[str(weeknum)] #获取当周所有课程
        weekdays = int(weekday) #根据当天是星期几读取当周课程对应的日期
        if weekdays == 1 :
            daynam = 'mon'
        elif weekdays ==2 :
            daynam = 'tue'
        elif weekdays ==3 :
            daynam = 'wed'
        elif weekdays ==4 :
            daynam = 'thu'
        elif weekdays ==5 :
            daynam = 'fri'
        else:
            print('erro')
        classlist = Cx.parse(weekclass_list[daynam]) #获取当天所有课程为列表
        dayclassresult = '\n' + '--------上   午--------' + '\n' + \
                          '第一、二节：' +'\n' + classlist[0] +'\n' + '****************************' +'\n' + \
                          '第三、节四：' +'\n' + classlist[1] +'\n'  + \
                          '--------下   午--------' + '\n' + \
                          '第一、二节：' +'\n' + classlist[2] +'\n' + '****************************' +'\n' + \
                          '第三、四节：' +'\n' + classlist[3] +'\n' + \
                          '--------晚   上--------' + '\n' + \
                          '第一、二节：' +'\n' + classlist[4] +'\n' + '****************************' +'\n' + \
                          '第三、四节：' +'\n' + classlist[5] + '\n' +'****************************'
        return dayclassresult



class Push:#结果推送类

    def __init__(self,qqres):#初始化
        self.qqres = qqres


    def qqtext(self):  # QQ推送，采用Qmsg酱http接口(若使用酷推等同类产品仅需改变host即可)
        host = 'https://qmsg.zendee.cn/send/' + qqkey + '?msg='  # 这里填Qmsg的推送地址
        url = host + self.qqres
        response = requests.post(url)
        print('QQ消息发送成功')




# -*- coding: UTF-8 -*-
# by sun
#use for tx cloud
#此脚本仅2021年3月1日后可正常运行

import datetime
import time
import prettytable as pt
import re
import requests
import smtplib 
from email.mime.text import MIMEText 
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import json


def main_handler(event, context):
    global qqkey
    global mailuser
    global mailpwd
    global mailreceiver
    #QQ推送设置
    qqkey = '' #这里填Qmsg的KEY
    
    #邮件推送设置
    mailuser = '' #这里填发送邮件的163邮箱账号
    mailpwd = '' #这里填邮箱的发送授权密码（不是登录密码）
    mailreceiver = '' #这里填邮件的接收邮箱，推荐填你的QQ邮箱

    
    
    global db
    global weeknum
    global weekday
    # 读取课表数据字典
    with open('data.json', 'r') as f:
        db = json.load(f)
        f.close()

    #2021.3.1日后用realdatetime替换datatime

    realdatetime = datetime.datetime.now().strftime('%Y-%m-%d')
    datatime = "2021-03-16"
    a = time.strptime(str(datatime), "%Y-%m-%d")
    y = a.tm_year
    m = a.tm_mon
    d = a.tm_mday
    sj = Shijian(y,m,d)#实例化一个时间类用于获取日期处于第几周星期几
    weeknum = sj.get_weeknum()
    weekday = sj.get_weekday()

    cx = Cx(weeknum, weekday)#实例化一个查询类
    if weekday == '0': #星期天提醒,仅推送一条qq消息
        qqres = '今天的日期是：' + datatime + '\n' +'第%s周'%(weeknum) + '星期日' + '\n' + '今天没有课！'
        mailres = ''
        push = Push(mailres,qqres,weeknum)#实例化推送类
        push.qqtext()

    elif weekday == '6':#星期六发送下周课表，邮箱推送课表，QQ推送提醒
        res1 = '今天的日期是：' + datatime + '\n' + '第%s周' % weeknum + '星期六' + '\n' + '休息日！' + '\n' + '下周的课程是：'
        res2 = cx.get_weekclass()
        mailres = res1 + res2
        qqres = '今天的日期是：' + datatime + '\n' + '第%s周' % weeknum + '星期六' + '\n' + '休息日！' + '\n' + '下周课表已发送到邮箱，请注意查收!'
        push = Push(mailres,qqres,weeknum)
        push.mailpic()
        push.qqtext()

    else:#星期一到星期五，推送每天当天课程，仅QQ推送
        res1 = '今天的日期是：' + datatime + '\n' + '第%s周' % weeknum + '星期%s'%weekday
        res2 = cx.get_dayclass()
        mailres = ''
        qqres = res1 +res2
        push = Push(mailres,qqres,weeknum)
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
        weekday = datetime.datetime(self.y,self.m,self.d).strftime("%w")
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

    def get_classname(weeklist):#提取出课程名称返回名称列表，用于建立每周课程表table
        re1 = r"课程名称:(.*?)\n教室"
        temp = []
        for each in weeklist:
            name1 = re.findall(re1, each)
            temp.append(name1)
        return temp

    def get_weekclass(self):#获取下周课程名称返回table
        weekclass_list = db[str(weeknum+1) ]
        mon = Cx.get_classname(Cx.parse(weekclass_list['mon']))
        tue = Cx.get_classname(Cx.parse(weekclass_list['tue']))
        wed = Cx.get_classname(Cx.parse(weekclass_list['wed']))
        thu = Cx.get_classname(Cx.parse(weekclass_list['thu']))
        fri = Cx.get_classname(Cx.parse(weekclass_list['fri']))
        tb = pt.PrettyTable()
        tb.add_column('',['  第一、二节  ','  第三、四节  ','  第五、六节  ','  第七、八节  ','  第九、十节  ',' 第十一、十二节 '])
        tb.add_column('星期一',mon)
        tb.add_column('星期二',tue)
        tb.add_column('星期三',wed)
        tb.add_column('星期四',thu)
        tb.add_column('星期五',fri)
        tb.add_column('',['','','','','',''])
        table = tb.get_html_string()
        return table

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

    def __init__(self,mailres,qqres,weeknum):#初始化区分邮件结果和QQ结果
        self.mailres = mailres
        self.qqres = qqres
        self.weeknum = weeknum

    def mailpic(self):#发送图片邮件,用于周六时发送下周课表图片到邮箱
        host = 'smtp.163.com'  # 发件服务器
        port = 994  # SSL发件端口
        sender = mailuser
        pwd = mailpwd
        receiver = mailreceiver
        text = self.mailres

        body = text
        msg = MIMEText(body,"html", "utf-8")

        message = MIMEMultipart()
        message['subject'] = '课程表'
        # 设置标题

        message['from'] = sender
        message['to'] = receiver

        message.attach(msg)
        filename = './pic/' + str(weeknum+1) + '.png' # 构造附件1，传送当前目录下的 filename 文件
        ctype = 'application/octet-stream'
        subtype = ctype.split('/', 1)
        att1 = MIMEImage(open(filename, 'rb').read(), _subtype=subtype)
        att1.add_header('Content-Disposition', 'attachment', filename='图片.jpg')
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        message.attach(att1)
        try:

            s = smtplib.SMTP_SSL(host, port)  # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
            s.login(sender, pwd)  # 登陆邮箱
            s.sendmail(sender, receiver, message.as_string())  # 发送邮件！
            print('发送成功')
            time.sleep(3)
        except smtplib.SMTPException:
            print('发送失败')

    def qqtext(self):  # QQ推送，采用Qmsg酱http接口(若使用酷推等同类产品仅需改变host即可)
        host = 'https://qmsg.zendee.cn/send/' + qqkey + '?msg='  # 这里填Qmsg的推送地址
        url = host + self.qqres
        response = requests.post(url)
        print('QQ消息发送成功')


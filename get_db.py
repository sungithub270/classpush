# -*- coding: UTF-8 -*-
# by sun
#用于获取课表数据，包括图片及课表字典

import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.select import Select
import re
import json

def get_class():
    user = ''
    pwd = ''

    url = 'http://jwgl.wfmc.edu.cn/jsxsd/xskb/xskb_list.do'
    driver.get(url)
    driver.find_element_by_xpath('//*[@id="userAccount"]').send_keys(user)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="userPassword"]').send_keys(pwd)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="ul1"]/li[4]/button').click()

    driver.execute_script('window.open()')
    windows = driver.window_handles
    driver.switch_to.window(windows[1])
    driver.get('http://jwgl.wfmc.edu.cn/jsxsd/xskb/xskb_list.do')

    Select(driver.find_element_by_xpath('//*[@id="xnxq01id"]')).select_by_value('2020-2021-2')


    result = {}#结果字典

    for weekno in range(1,20):



        Select(driver.find_element_by_xpath('//*[@id="zc"]')).select_by_index(int(weekno))

        picname = str(weekno) + '.png'
        width = driver.execute_script("return document.documentElement.scrollWidth")
        height = driver.execute_script("return document.documentElement.scrollHeight")
        #print(width, height)#获取宽和高
        driver.set_window_size(width, height)
        #driver.save_screenshot(picname)#保存课表图片


        html = driver.page_source
        soup = BeautifulSoup(html,'lxml')
        target = soup.find_all('div', class_ = 'kbcontent')
        km = []
        room = []
        ls = []
        zc = []



        for each in target:
            re1 = r'style="">(.*?)<br/>'
            re2 = r'<font title="教室">(.*?)</font>'
            re3 = r'<font title="老师">(.*?)</font>'
            re4 = r'<font title="周次\(节次\)">(.*?)</font>'

            km_ = re.findall(re1,str(each))
            room_ = re.findall(re2,str(each))
            ls_ = re.findall(re3,str(each))
            zc_ = re.findall(re4,str(each))

            km.append(km_)
            room.append(room_)
            ls.append(ls_)
            zc.append(zc_)


        kb = [] #每周课表，共42节
        eachweek = {}#每周字典

        for a in range(42):
            temp = '课程名称:' + str(km[a]).replace('[','').replace(']','').replace("'",'').replace("'",'') + '\n' + '教室:' + str(room[a]).replace('[','').replace(']','').replace("'",'').replace("'",'') + '\n' + '老师:' + str(ls[a]).replace('[','').replace(']','').replace("'",'').replace("'",'') + '\n' + '周次:' + str(zc[a]).replace('[','').replace(']','').replace("'",'').replace("'",'')
            kb.append(temp)
        #print(kb)

        mon = []
        tue = []
        wed = []
        thu = []
        fri = []




        mon.append(kb[0])
        mon.append(kb[7])
        mon.append(kb[14])
        mon.append(kb[21])
        mon.append(kb[28])
        mon.append(kb[35])
        tue.append(kb[1])
        tue.append(kb[8])
        tue.append(kb[15])
        tue.append(kb[22])
        tue.append(kb[29])
        tue.append(kb[36])
        wed.append(kb[2])
        wed.append(kb[9])
        wed.append(kb[16])
        wed.append(kb[23])
        wed.append(kb[30])
        wed.append(kb[37])
        thu.append(kb[3])
        thu.append(kb[10])
        thu.append(kb[17])
        thu.append(kb[24])
        thu.append(kb[31])
        thu.append(kb[38])
        fri.append(kb[4])
        fri.append(kb[11])
        fri.append(kb[18])
        fri.append(kb[25])
        fri.append(kb[32])
        fri.append(kb[39])

       


        eachweek['mon'] = mon
        eachweek['tue'] = tue
        eachweek['wed'] = wed
        eachweek['thu'] = thu
        eachweek['fri'] = fri
        result[int(weekno)] = eachweek


    #保存课表字典为json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f)
    #print(result)



if __name__ == '__main__':

    option = ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-gpu')
    option.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=option)

    get_class()

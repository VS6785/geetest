#!/usr/bin/env python
# __*__ coding: utf-8 __*__

""" 
__author__: lazy
@file: geetest.py 
@time: 2019/03/03 
@func: slide break ,correct rate 85%
"""

# -*-coding:utf-8 -*-
import random
import re
import time
import redis
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import PIL.Image as image
from bwjf_scrapy.middlewares import user_agents
from redis.sentinel import Sentinel
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from bwjf_scrapy.util.webdriver_util import WebdriverUtil
# from eie_info.settings import IP_PROXY

# PROXIES = [{'host': '118.81.72.164', 'port': 9797}, {'host': '111.177.166.226', 'port': 9999},
#            {'host': '101.236.42.63', 'port': 8866}, {'host': '114.99.253.216', 'port': 8118},
#            {'host': '111.177.188.61', 'port': 9999}, {'host': '116.211.91.134', 'port': 8080},
#            {'host': '221.2.174.3', 'port': 8060}]


# pool=redis.ConnectionPool(host= IP_PROXY,port=6379,db=8)
# r = redis.StrictRedis(connection_pool=pool)
from redis.sentinel import Sentinel

sentinel = Sentinel([('10.101.3.177', 26379),('10.101.3.178', 26379),('10.101.3.179', 26379)],socket_timeout=5)
r = sentinel.master_for('mymaster', socket_timeout=5, db=8)
PROXIES = r.srandmember("proxies", 1)
proxy = PROXIES[0].decode('utf-8')
PROXY = {}
PROXY['host'] = eval(proxy)['ip']
PROXY['port'] = eval(proxy)['port']

class Crack():
    def __init__(self, url, word, searchId, bowtonID):
        self.url = url
        # proxy = random.choice(PROXIES)
        # 打开带配置信息的phantomJS浏览器
        # self.browser = webdriver.PhantomJS()
        # self.browser = webdriver.Chrome()
        self.browser = WebdriverUtil().getWebDriverHeadLess(proxyip=PROXY,types=None)
        self.wait = WebDriverWait(self.browser, 60)
        self.word = word
        self.searchId = searchId
        self.bowtonID = bowtonID
        self.BORDER = 7

    def open(self):
        """
        # 打开浏览器,并输入查询内容
        """
        self.browser.maximize_window()
        self.browser.get(self.url)
        self.browser.implicitly_wait(10)
        ## 上海
        # keyword = self.wait.until(EC.presence_of_element_located((By.ID, 'keyword')))
        # bowton = self.wait.until(EC.presence_of_element_located((By.ID, 'buttonSearch')))
        ## 湖北
        # keyword = self.wait.until(EC.presence_of_element_located((By.ID, 'searchText')))
        # bowton = self.wait.until(EC.presence_of_element_located((By.ID, 'click')))
        ## 黑龙江
        # keyword = self.wait.until(EC.presence_of_element_located((By.ID, 'searchText')))
        # bowton = self.wait.until(EC.presence_of_element_located((By.ID, 'click')))
        ## params
        try:
            keyword = self.wait.until(EC.presence_of_element_located((By.ID, self.searchId)))
        except:
            keyword = self.wait.until(EC.presence_of_element_located((By.ID, self.searchId)))
        times = [0.5, 0.62, 0.75]
        time.sleep(random.choice(times))
        try:
            bowton = self.wait.until(EC.presence_of_element_located((By.ID, self.bowtonID)))
        except:
            bowton = self.wait.until(EC.presence_of_element_located((By.ID, self.bowtonID)))
        try:
            keyword.send_keys(self.word)
        except:
            keyword.send_keys(self.word)
        try:
            bowton.click()
        except:
            bowton.click()

    def get_images(self, bg_filename='bg.jpg', fullbg_filename='fullbg.jpg'):
        """
        获取验证码图片
        :return: 图片的location信息
        """
        bg = []
        fullgb = []
        while bg == [] and fullgb == []:
            bf = BeautifulSoup(self.browser.page_source, 'lxml')
            bg = bf.find_all('div', class_='gt_cut_bg_slice')
            fullgb = bf.find_all('div', class_='gt_cut_fullbg_slice')
        try:
            bg_url = re.findall('url\(\"(.*)\"\)', bg[0].get('style'))[0].replace('webp', 'jpg')
            fullgb_url = re.findall('url\(\"(.*)\"\)', fullgb[0].get('style'))[0].replace('webp', 'jpg')
        except:
            bg_url = re.findall('(http://static.geetest.com/pictures/gt/.*?jpg|http://static.geetest.com/pictures/gt/.*?webp)', bg[0].get('style'))[0].replace('webp', 'jpg')
            fullgb_url = re.findall('(http://static.geetest.com/pictures/gt/.*?jpg|http://static.geetest.com/pictures/gt/.*?webp)', fullgb[0].get('style'))[0].replace('webp', 'jpg')
        bg_location_list = []
        fullbg_location_list = []
        for each_bg in bg:
            location = {}
            location['x'] = int(re.findall('background-position: (.*)px (.*)px', each_bg.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px', each_bg.get('style'))[0][1])
            bg_location_list.append(location)
        for each_fullgb in fullgb:
            location = {}
            location['x'] = int(re.findall('background-position: (.*)px (.*)px', each_fullgb.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px', each_fullgb.get('style'))[0][1])
            fullbg_location_list.append(location)

        urlretrieve(url=bg_url, filename=bg_filename)
        urlretrieve(url=fullgb_url, filename=fullbg_filename)
        return bg_location_list, fullbg_location_list

    def get_merge_image(self, filename, location_list):
        """
        根据位置对图片进行合并还原
        :filename:图片
        :location_list:图片位置
        """
        im = image.open(filename)
        new_im = image.new('RGB', (260, 116))
        im_list_upper = []
        im_list_down = []

        for location in location_list:
            if location['y'] == -58:
                im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
            if location['y'] == 0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

        new_im = image.new('RGB', (260, 116))

        x_offset = 0
        for im in im_list_upper:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]

        new_im.save(filename)

        return new_im

    def get_merge_image(self, filename, location_list):
        """
        根据位置对图片进行合并还原
        :filename:图片
        :location_list:图片位置
        """
        im = image.open(filename)
        new_im = image.new('RGB', (260, 116))
        im_list_upper = []
        im_list_down = []

        for location in location_list:
            if location['y'] == -58:
                im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
            if location['y'] == 0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

        new_im = image.new('RGB', (260, 116))

        x_offset = 0
        for im in im_list_upper:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]

        new_im.save(filename)

        return new_im

    def is_pixel_equal(self, img1, img2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        threshold = 80
        if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(
                pix1[2] - pix2[2] < threshold)):
            return True
        else:
            return False

    def get_gap(self, img1, img2):
        """
        获取缺口偏移量
        :param img1: 不带缺口图片
        :param img2: 带缺口图片
        :return:
        """
        left = 43
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 经过实验分析，考虑滑动距离太短对正确率的影响，故阈值增加了elif的策略
        if distance < 80:
            # 减速阈值
            ms = [0.4,0.45, 0.5]
            m = random.choice(ms)
            mid = distance * m
            # 计算间隔
            t = 0.2
            # 初速度
            v = 0
            while current < distance:
                if current < mid:
                    # 设置加速度动态变化
                    # an = [2.1, 2.3, 2.5, 2.7, 2.9, 2, 2.2, 2.4, 2.6, 2.8, 1.9, 1.8, 1.7, 1.6]
                    an = [3,]
                    a = random.choice(an)
                else:
                    # 设置减速度动态变化
                    ap = [-3.6,-3.5]
                    # ap = [-2.8,-3.4,-3.1,-2.7,-2.6,-2.9,-3,-3.2,-3.3,-3.5,-3.1,-2.1,-2.2,-2.3,-2.4,-2.5]
                    a = random.choice(ap)
                # 初速度v0
                v0 = v
                v = v0 + a * t
                move = v0 * t + 1 / 2 * a * t * t
                # 当前位移
                current += move
                # 加入轨迹
                track.append(round(move))
                if len(track) < 60:
                    track =track + [0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0,0, 0, 0, 0, 0,0, 0, 0, 0, 0,0, 0, 0]
                elif len(track) >100:
                    track = track[50:150]
                else:
                    track = track
        elif  distance > 80:
            ms = [0.7, 0.8, 0.75, 0.6, 0.62, 0.64, 0.66, 0.68, 0.72, 0.74, 0.76, 0.78]
            m = random.choice(ms)
            mid = distance *m
            # 计算间隔
            t = 0.2
            # 初速度
            v = 0
            while current < distance:
                if current < mid:
                    # 设置加速度动态变化
                    # Chrome 浏览器的加速度
                    # an = [2.1,2.3,2.5,2.7,2.9,2,2.2,2.4,2.6,2.8,1.9,1.8,1.7,1.6]
                    an = [4,]
                    a = random.choice(an)
                else:
                    # 设置减速度动态变化
                    # Chrome 浏览器的减速度
                    ap = [-5,-4.9]
                    a = random.choice(ap)
                # 初速度v0
                v0 = v
                v = v0 + a * t
                move = v0 * t + 1 / 2 * a * t * t
                # 当前位移
                current += move
                # 加入轨迹
                track.append(round(move))
                if len(track) < 45:
                    track = track + [0, 0, 0, 0, 0, 0]
                else:
                    track = track
        return track

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        while True:
            try:
                slider = self.browser.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
                break
            except:
                time.sleep(0.3)
        return slider

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        while track:
            for t in track:
                x = t
                ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
                track.remove(x)
        # time.sleep(0.12)
        # ActionChains(self.browser).move_by_offset(xoffset=-3, yoffset=0).perform()
        # ActionChains(self.browser).move_by_offset(xoffset=3, yoffset=0).perform()
        # time.sleep(0.21)
        # ActionChains(self.browser).release().perform()

    def crack(self):
        # 打开浏览器
        self.open()
        # 保存的图片名字
        bg_filename = 'bg.jpg'
        fullbg_filename = 'fullbg.jpg'

        # 获取图片
        bg_location_list, fullbg_location_list = self.get_images(bg_filename, fullbg_filename)

        # 根据位置对图片进行合并还原
        bg_img = self.get_merge_image(bg_filename, bg_location_list)
        fullbg_img = self.get_merge_image(fullbg_filename, fullbg_location_list)

        # 获取缺口位置
        gap = self.get_gap(fullbg_img, bg_img)
        track = self.get_track(gap - self.BORDER)
        # print('轨迹：',len(track),track)
        # # 点按呼出缺口
        slider = self.get_slider()
        # # 拖动滑块到缺口处
        time.sleep(random.randint(6,15)/10)
        self.move_to_gap(slider, track)
        time.sleep(random.randint(10, 14) / 10)
        ActionChains(self.browser).move_by_offset(xoffset=-3, yoffset=0).perform()
        ActionChains(self.browser).move_by_offset(xoffset=3, yoffset=0).perform()
        time.sleep(random.randint(18, 29) / 10)
        ActionChains(self.browser).release().perform()
        time.sleep(3.5)
        html = self.browser.page_source
        if '查询' in html:
            self.browser.quit()
            return html
        else:
            if len(self.word) == 2:
                element = self.browser.find_element_by_xpath('//a[@class="gt_refresh_button"]')
                element.click()
                print("again times")
                html = self.crack()
                self.browser.quit()
            else:
                self.browser.quit()
            return html

from lxml import etree
from pyquery import PyQuery as pq
if __name__ == '__main__':
    i = 2
    correct = 0
    ## 黑龙江
    # url = 'http://gsxt.hljaic.gov.cn/index.jspx'
    ## 吉林
    url = 'http://211.141.74.200/'
    ## 上海
    # url = 'http://www.sgs.gov.cn/notice/home'
    ## 湖北
    # url = 'http://xygs.egs.gov.cn/index.jspx'
    while i > 0:
        i = i-1
        crack = Crack(url=url, word='百度', searchId='txtSearch', bowtonID='btnSearch')
        html = crack.crack()
        if "查询" in html:
            print('OK!')
            uuids = re.findall('<a class="m-searchresult-name" href="(.*?)">.*?</a>', html, re.S)
            soup = BeautifulSoup(html, 'lxml')
            names = soup.select('a[class="m-searchresult-name"]')
            for i, j in zip(names, uuids):
                name = i.text.strip()
                url = ('http://211.141.74.200/' + j.strip()).replace('amp;', '')
                print(name, url)
            correct = correct + 1
            print('Sucess time:',correct)
    print('滑动破解正确率：',correct/2)
# -*- coding: utf-8 -*-
import Parser

import urllib2
import urllib
import cookielib

import lxml.html as HTML
from lxml import etree
import lxml
import sys

import time
#from datetime import *
import re
import pymongo
from pymongo import MongoClient
import json

class Fetcher(object):
    def __init__(self, username=None, pwd=None, cookie_filename=None):
        self.cj = cookielib.LWPCookieJar()
        if cookie_filename is not None:
            self.cj.load(cookie_filename)
        self.cookie_processor = urllib2.HTTPCookieProcessor(self.cj)
        self.opener = urllib2.build_opener(self.cookie_processor, urllib2.HTTPHandler)
        urllib2.install_opener(self.opener)
         
        self.username = username
        self.pwd = pwd
        #self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
        #                'Referer':'','Content-Type':'application/x-www-form-urlencoded'}
        self.headers = {'User-Agent': 'Mozilla/5.0 (MSIE 9.0; Windows NT 6.3; WOW64; Trident/7.0; MALNJS; rv:11.0) like Gecko'}
    def get_rand(self, url):
        #headers = {'User-Agent':'Mozilla/5.0 (Windows;U;Windows NT 5.1;zh-CN;rv:1.9.2.9)Gecko/20100824 Firefox/3.6.9',
        #           'Referer':''}
        headers = {'User-Agent': 'Mozilla/5.0 (MSIE 9.0; Windows NT 6.3; WOW64; Trident/7.0; MALNJS; rv:11.0) like Gecko'}
        req = urllib2.Request(url ,urllib.urlencode({}), headers)
        resp = urllib2.urlopen(req)
        login_page = resp.read()
        rand = HTML.fromstring(login_page).xpath("//form/@action")[0]
        passwd = HTML.fromstring(login_page).xpath("//input[@type='password']/@name")[0]
        vk = HTML.fromstring(login_page).xpath("//input[@name='vk']/@value")[0]
        return rand, passwd, vk

    def login(self, username=None, pwd=None, cookie_filename=None, delay=0.0):
        if self.username is None or self.pwd is None:
            self.username = username
            self.pwd = pwd
        assert self.username is not None and self.pwd is not None
         
        url = 'https://login.weibo.cn/login/?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt='
        rand, passwd, vk = self.get_rand(url)
        data = urllib.urlencode({'mobile': self.username,
                                 passwd: self.pwd,
                                 'remember': 'on',
                                 'backURL': 'http://weibo.cn/',
                                 #'backURL': 'http%3A%2F%2Fweibo.cn%2F',
                                 'backTitle': '微博',   #'\xe5\xbe\xae\xe5\x8d\x9a'
                                 'tryCount': '',
                                 'vk': vk,
                                 'submit':'登录'})  #'\xe7\x99\xbb\xe5\xbd\x95'
        url = 'https://login.weibo.cn/login/' + rand
        req = urllib2.Request(url, data, self.headers)
        resp = urllib2.urlopen(req)
        
        redirecturl = resp.geturl() #获取重定向页面的url
        req = urllib2.Request(redirecturl,data,self.headers)
        resp = urllib2.urlopen(req) #得到重定向页面
        page = resp.read()  #得到重定向地址
        link = HTML.fromstring(page).xpath("//a/@href")[0]
        if not link.startswith('http://'): link = 'http://weibo.cn/%s' % link
        req = urllib2.Request(link, headers=self.headers)
        page = urllib2.urlopen(req).read()
        if cookie_filename is not None:
            self.cj.save(filename=cookie_filename)
        elif self.cj.filename is not None:
            self.cj.save()
        print 'login process finished.'
        self.PageDelay = delay  #设定延时时间
         
    def fetch(self, url):
        #print 'fetch url: ', url
        req = urllib2.Request(url, headers=self.headers)
        content = urllib2.urlopen(req).read()
        #print 'unicode: ', content
        time.sleep(self.PageDelay)
        return content

    def ErrorPage(self,tree):
        #Deal with error page.
        if not tree:
            print "Error occured in ErrorPage loading."
            sys.exit()
        subtree = tree.xpath("//div[@class='c']/text()")
        ErrorFlag = False
        ErrorClueCount = 0
        for branch in subtree:
            if re.search(r'帐号[\S]*异常[\S]*无法访问',branch) or re.search(r'解除[\S]*访问[\S]*限制',branch) or re.search(r'在线[\S]*申诉',branch):
                ErrorClueCount = ErrorClueCount + 1
        if ErrorClueCount >1:
            ErrorFlag = True
        if ErrorFlag:
            print "Account exception error occurred! Try to change another one and restart."
            return False
        else:
            return True

    def UserPreParser(self,url):
        #Crawls the main page of a user to get the uid and other information.
        #Stores information in mongo.
        currTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) #Current time.
        content = self.fetch(url)
        tree = etree.HTML(content)
        UserTree = tree.xpath("/html/body/div[@class='u']")
        UPnBI = UserTree[0].xpath("./table/tr/td") #UPnBI[0]:User Portrait, UPnBI[1] Basic Info.

        UP = UPnBI[0].xpath("./a")
        tempRem = UP[0].attrib['href'].split('/')[1]
        if len(tempRem)>0 and re.match(r'\d+',tempRem):                 ##ID of current user.
            currID = tempRem
        else:
            currID = None

        BI = UPnBI[1].xpath("./div")
        UserIntros = BI[0].xpath("./span")
        UserIntroOne = UserIntros[0].xpath("./text()")
        for i in range(len(UserIntroOne)):
            if len(UserIntroOne[i])>0:  UserIntroOne[i] = UserIntroOne[i].strip().replace(u"\xa0",'')
        UserName = re.sub(r'\[在线\]','',UserIntroOne[0])   #User nick name.
        UserSex,UserLocation = UserIntroOne[2].split(u'/')  #Sex and City.
        UserRank = UserIntros[0].xpath("./a[@href='/" + currID + "/urank']")[0].text  #User rank: xxx级.
        if len(UserIntros)>1:
            OtherIntros = []
            for i in range(1, len(UserIntros)): #Authentication and brief Self-intro.
                OtherIntros.append(UserIntros[i].text)
        #Statistics:
        StatTree = UserTree[0].xpath("./div/*")
        TweetCount = re.search(r'[0-9]+',StatTree[0].text).group()  #Number of Tweets.
        FollowsNum = re.search(r'[0-9]+',StatTree[1].text).group()  #Number of Users followed by current user.
        FansNum = re.search(r'[0-9]+',StatTree[2].text).group()     #Number of followers.
        PubGroupNum = re.search(r'[0-9]+',StatTree[3].text).group() #Number of public groups.
        Statistics = {"user_tweet_num":TweetCount,
                      "user_follow_num":FollowsNum,
                      "user_fans_num":FansNum,
                      "user_group_num":PubGroupNum}

        data = {"user_id":currID,
                "user_nickname":UserName,
                "user_sex":UserSex,
                "user_location":UserLocation,
                "user_rank":UserRank,
                "user_intro_short":OtherIntros,
                "user_stat":Statistics,
                "crawlpage_time":currTime}
        #data = {"Basic":post,
        #        "Statistics":Statistics}
        data = json.dumps(data)
        
        #client = MongoClient()
        #db = client.Sina_test
        #UserPage = db.User_Page
        #Create User_Page with unique user id.
        #if not UserPage.find_one({"user_id":currID}):
        #    UserPage.insert(post)
        #else:
        #    UserPage.update({"user_id":currID},post)
        #client.close()
        return data


    def UserFollowPageParser(self,uid):
        #client = MongoClient()  #Mongodb config.
        #db = client.Sina_test
        #UserPage = db.User_Page
        FinishFlag = False
        NamePairRem = []
        pageIndex = 0
        while not FinishFlag:
            #Open next page.
            content = self.fetch('http://weibo.cn/' + str(uid) + '/follow?page=' + str(int(pageIndex)+1))
            UserFollowTree = etree.HTML(content)
            pageindexTree = UserFollowTree.xpath("./body/div[@id='pagelist']/form/div/text()")
            for i in range(0,len(pageindexTree)):
                if len(pageindexTree[i])>0:
                    pageindexTree[i] = pageindexTree[i].strip().replace(u'\xa0','')
                    if isinstance(pageindexTree[i],unicode):
                        if len(pageindexTree[i])>0 and re.search(r'[0-9]+/[0-9]+',pageindexTree[i]):
                            indexes = re.search(r'[0-9]+/[0-9]+',pageindexTree[i]).group()
                            break
            pageIndex,pageCount = indexes.split(u"/")       #Set index and count of the current page.
            if pageIndex == pageCount:
                FinishFlag = True                           #Flag set.
            #Start crawling current page.
            subUFT = UserFollowTree.xpath("./body/table")   #Sub tree of (U)ser(F)ollow(T)ree
            for branch in subUFT:
                leaf = branch.xpath("./tr/td/a")
                UserMainPageLink = leaf[0].attrib['href']   #Link of the main page of a followed user(str).
                #if isinstance(UserMainPageLink,unicode):
                #    UserMainPageLink = UserMainPageLink.encode('utf-8')
                if '?' in UserMainPageLink:
                    UserMainPageLink,rubbish = UserMainPageLink.split("?")
                UserName = leaf[1].text                     #User name(default:'unicode',encoded into 'utf-8').
                #if isinstance(UserName,unicode):
                #    UserName = UserName.encode("utf-8")
                NamePairRem.append([UserName,UserMainPageLink])
        return  NamePairRem

    def UserFansPageParser(self,uid):
        #Crawls one page according to uid and pagenum
        #client = MongoClient()  #Mongodb config.
        #db = client.Sina_test
        #UserPage = db.User_Page
        FinishFlag = False
        UserInfoRem = []
        pageIndex = 0
        while not FinishFlag:
            #Open page.
            content = self.fetch('http://weibo.cn/' + str(uid) + '/fans?page=' + str(int(pageIndex) + 1))
            UserFansTree = etree.HTML(content)
            pageindexTree = UserFansTree.xpath("./body/div[@class='c']/div[@id='pagelist']/form/div/text()")
            for i in range(0,len(pageindexTree)):
                if len(pageindexTree[i])>0:
                    pageindexTree[i] = pageindexTree[i].strip().replace(u'\xa0','')
                    if isinstance(pageindexTree[i],unicode):
                        if len(pageindexTree[i])>0 and re.search(r'[0-9]+/[0-9]+',pageindexTree[i]):
                            indexes = re.search(r'[0-9]+/[0-9]+',pageindexTree[i]).group()
                            break
            pageIndex,pageCount = indexes.split(u"/")       #Set index and count of the current page.
            if pageIndex == pageCount:
                FinishFlag = True                           #Flag set.
            #Start crawling current page.
            subUserFansTree = UserFansTree.xpath("./body/div[@class='c']/table")
            for user in subUserFansTree:
                UserLeaf = user.xpath("./tr/td")
                UserMainPageLink,rubbish = UserLeaf[0].xpath("./a")[0].attrib['href'].split('?')    #Link of the main page of a fans.
                #UserID = re.sub('http://weibo.cn/u/','',UserMainPageLink)                           #ID of fans.
                UserName = UserLeaf[1].xpath("./a")[0].text                                         #User nick name(default:'unicode',encoded into 'utf-8').
                UserInfoRem.append([UserName,UserMainPageLink])

            data = u"{"
            for i in range(0,len(UserInfoRem)):
                data = data + u'\'fans_nickname\'' + u":" + UserInfoRem[i][0] + u","
                #data = data + '\'fans_id\'' + ":" + UserInfoRem[i][1] + ","
                data = data + u'\'fans_link\'' + u":" + UserInfoRem[i][1] + u","
            data = data[0:-1] + "}"
            data = json.dumps(data)
        return data

    def UserContentPageParser(self,uid):
        #Crawls one page according to uid and pagenum
        #client = MongoClient()  #Mongodb config.
        #db = client.Sina_test
        #UserPage = db.User_Page
        FinishFlag = False
        UserContent = []
        pageIndex = 0
        while not FinishFlag:
            #Open page.
            content = self.fetch('http://weibo.cn/' + str(uid) + '?page=' + str(int(pageIndex) + 1))
            UserContentTree = etree.HTML(content)
            pageindexTree = UserContentTree.xpath("./body/div[@id='pagelist']/form/div/text()")
            for i in range(0,len(pageindexTree)):
                if len(pageindexTree[i])>0:
                    pageindexTree[i] = pageindexTree[i].strip().replace(u'\xa0','')
                    if isinstance(pageindexTree[i],unicode):
                        if len(pageindexTree[i])>0 and re.search(r'[0-9]+/[0-9]+',pageindexTree[i]):
                            indexes = re.search(r'[0-9]+/[0-9]+',pageindexTree[i]).group()
                            break
            pageIndex,pageCount = indexes.split(u"/")       #Set index and count of the current page.
            if pageIndex == pageCount:
                FinishFlag = True                           #Flag set.
            #Start crawling current page.
            currTweetCount = UserContentTree.xpath("./body/div[@class='s']")
            currTweetTree = UserContentTree.xpath("./body/div[@class='c']")
            UserContent.append(self.TweetParser(currTweetTree))
        return UserContent

    '''
    下面这段需要立刻重写,每一种情况的tweet需要专门写一个解析函数，否则本段代码太长，而且不一定写在本文件中
    '''
    def TweetParser(self,TweetTree):
        #Parse one tweet by one call.
        #Called by UserContentPageParser()
        PageContent = []
        if len(TweetTree) > 2:
            TweetTree = TweetTree[0:-2]
            for tweetBranch in TweetTree:
                PageContent.append(Parser.TweetContentParser(tweetBranch))
        return PageContent

# -*- coding: utf-8 -*-
from Login import Fetcher
from Config import PreConfig

from lxml import etree
import lxml
import lxml.html.soupparser as sper
 
import re

PreConfiger = PreConfig()
PreConfiger.LoginInfoSet()
username,password = PreConfiger.LoginInfoGet()

LogIner = Fetcher()
LogIner.login(username, password, 'cookies.lwp')
#LogIner.UserPreParser('http://weibo.cn/1848612965')
#LogIner.UserFansPageParser('1848612965')
#LogIner.UserFollowPageParser('1848612965')
LogIner.UserContentPageParser('1743826334')

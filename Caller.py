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
LogIner.login("smallyangy@163.com", "half0101155753", 'cookies.lwp')
#LogIner.UserPreParser('http://weibo.cn/1848612965')
#LogIner.UserFansPageParser('1848612965')
#LogIner.UserFollowPageParser('1848612965')
#LogIner.UserContentPageParser('1743826334')
LogIner.UserInfoParser('3700587630')

#content = LogIner.fetch('http://weibo.cn/xiena?page=1')
#tree = etree.HTML(content)
#subtree = tree.xpath("//p/text()|//p/a")

        
#NewSubTree = tree.xpath(u"//div[@id='plc_main']")
#NewSubTree[0].xpath("//*")
#new = tree.xpath(u"//script")
#new[14].text
#print LogIner.fetch('http://weibo.cn/1875333245/follow?page=2')
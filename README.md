#Weibo_CN_Crawler
================
##Version 1.0: 
----------------
###Feature: 
1. By replacing fuction LogIner.* in Caller.py to crawl corresponding weibo page. 

###To do list:<br>
1. Engineering control.
2. Data storage(MongoDB).
3. Debugging.

##Version 1.1: 
----------------
###Feature: 
1. Parsers are called sequentially biy func starter() from MongoTest.py
2. MongoDB support.<br>
>2.1 DB name: SinaTest<br>
>2.2 DB collections: <br>
    >>PreParser -- Basic info from main page of target user. <br>
    >>UserFans -- Fans of target user. <br>
    >>UserFollow -- users followed by target user. <br>
    >>UserContent -- Tweets of target user. <br>
    >>UserInfo -- Info page of target user. <br>
    >>Abnormity -- Users of abnormal account. <br>
    >>Candidate -- Users to be parsed.<br>
    >>Finished -- Users have been parsed.<br>
3. Sina login account are called in a circular queue, the queue is listed from my.yaml["login"]

###To do list:<br>
1. Parallism.<br>
2. Proxy.<br>

import yaml
import sys
import os
import json
import re
import time

def TweetContentParser(TweetBranch):
    '''
    data = {
        "MainTweet":
        {
            "Content":TweetContents,
            "Theme":TweetTheme(list),
            "At":TweetAt(list),
            "Time":TweetTime,
            "Device":TweetDevice,
            "Praise":TweetPraise,
            "RetweetTimes":TweetTimes,
            "Comment":TweetComment},
       "RetTweet":
       {
           "Content":RetweetedTweetContent,
           "Theme":RetweetedTweetTheme(list),
           "At":RetweetedTweetAt(list),
           "Praise":RetTweetPraise,
           "RetweetTimes":RetTweetTimes,
           "Comment":RetTweetComment,
           "SourceName":RetweetedTweetSource_Name,
           "SourceLink":RetweetedTweetSource_Link}
       }
    '''
    post = {
        "MainTweet":
        {
            "Content":'',
            "Theme":[],
            "At":[],
            "Time":'',
            "LocationName":'',
            "LocationLink":'',
            "Device":'',
            "Praise":'',
            "RetweetTimes":'',
            "Comment":''},
       "RetTweet":
       {
           "Content":'',
           "Theme":[],
           "At":[],
           "Praise":'',
           "RetweetTimes":'',
           "Comment":'',
           "SourceName":'',
           "SourceLink":''}
       }
    if len(TweetBranch) == 1:        #1.Text tweet only.
        TweetContents = TweetBranch[0].xpath("./span[@class='ctt']/text()")
        TweetContent = ''
        for content in TweetContents:
            if content is not None and len(content)>0:
                TweetContent = TweetContent + content.strip().replace(u'\xa0','')                   #Tweet content.
        subTweetBranch = TweetBranch[0].xpath("./span[@class='ctt']")[0]
        TweetLocation_name,TweetLocation_link = LocationParser(subTweetBranch,TweetContent)         #Location name, location link.
        TweetTheme,TweetAt = TweetThemeAtParser(subTweetBranch)                                     #Theme & At.
        DevnTimeNode = TweetBranch[0].xpath("./span[@class='ct']")[0]                               #Tweet time & Device that posts tweet.
        TweetTime,TweetDevice = DevicenTimeParser(DevnTimeNode)
        #TweetState = TweetBranch[0].xpath("./div")
        TweetPraise,TweetRetweet,TweetComment = TweetPraiseCommentRetweetParser(TweetBranch[0])     #Praise,Retweet Comment count.
        post["MainTweet"]["Content"] = TweetContent
        post["MainTweet"]["Theme"] = TweetTheme
        post["MainTweet"]["At"] = TweetAt
        post["MainTweet"]["Time"] = TweetTime
        post["MainTweet"]["LocationName"] = TweetLocation_name
        post["MainTweet"]["LocationLink"] = TweetLocation_link
        post["MainTweet"]["Device"] = TweetDevice
        post["MainTweet"]["Praise"] = TweetPraise
        post["MainTweet"]["RetweetTimes"] = TweetRetweet
        post["MainTweet"]["Comment"] = TweetComment
    elif len(TweetBranch) == 2:
        if len(TweetBranch[0].xpath("./span[@class='cmt']")) > 0:
            ReTweets = TweetBranch[0].xpath("./span[@class='cmt']/text()")
            ReTweetFlag = False
            ReTweetReasonFlag = False
            for retweet in ReTweets:
                if re.search(u'转发了',retweet):
                    ReTweetFlag = True
            ReTweetReason = TweetBranch[1].xpath("./span[@class='cmt']/text()")
            for reason in ReTweetReason:
                if re.search(u'转发理由',reason):
                    ReTweetReasonFlag = True
            #Retweet only text, no pic.
            if ReTweetFlag and ReTweetReasonFlag:
                #Get retweets.
                RetTweet = TweetBranch[0].xpath("./span[@class='cmt']")
                RetTweetSource_Name = RetTweet[0].xpath("./a")[0].text                              #Retweeted source info: nick name.
                RetTweetSource_Link,rubbish = RetTweet[0].xpath("./a")[0].attrib['href'].split('?') #Retweeted source info: main page link.
                RetTweetContents = TweetBranch[0].xpath("./span[@class='ctt']/text()")              #Retweeted content.
                RetTweetContent = ''
                for content in RetTweetContents:
                    if content is not None and len(content)>0:
                        RetTweetContent = RetTweetContent + content.strip().replace(u'\xa0','')
                RetTweetPraise,RetTweetTimes,RetTweetComment = TweetPraiseCommentRetweetParser(TweetBranch[0])#Praise,times,comment count
                subTweetBranch = TweetBranch[0].xpath("./span[@class='ctt']")[0]
                RetTweetTheme,RetTweetAt = TweetThemeAtParser(subTweetBranch)                       #Retweeted Theme & At
                post["RetTweet"]["SourceName"] = RetTweetSource_Name
                post["RetTweet"]["SourceLink"] = RetTweetSource_Link
                post["RetTweet"]["Content"] = RetTweetContent
                post["RetTweet"]["Praise"] = RetTweetPraise
                post["RetTweet"]["RetweetTimes"] = RetTweetTimes
                post["RetTweet"]["Comment"] = RetTweetComment
                post["RetTweet"]["Theme"] = RetTweetTheme
                post["RetTweet"]["At"] = RetTweetAt
                #Get tweets.
                Tweet = TweetBranch[1].xpath("./span[@class='cmt']")
                TweetContents = TweetBranch[1].xpath("./text()")                                                #Tweet content.
                TweetContent = ""
                for content in TweetContents:
                    if content is not None and len(content)>0:
                        TweetContent = TweetContent + content.strip().replace(u'\xa0','')
                DevnTimeNode = TweetBranch[1].xpath("./span[@class='ct']")[0]                                   #Tweet time & Device that posts tweet.
                TweetTime,TweetDevice = DevicenTimeParser(DevnTimeNode)
                subTweetBranch = TweetBranch[1].xpath("./*")[0]
                TweetTheme,TweetAt = TweetThemeAtParser(subTweetBranch)                                         #Theme & At
                TweetLocation_name,TweetLocation_link = LocationParser(subTweetBranch,TweetContent)             #Location name, location link.
                TweetPraise,TweetRetweet,TweetComment = TweetPraiseCommentRetweetParser(TweetBranch[1])         #Praise,Retweet Comment count.
                post["MainTweet"]["Content"] = TweetContent
                post["MainTweet"]["Theme"] = TweetTheme
                post["MainTweet"]["At"] = TweetAt
                post["MainTweet"]["Time"] = TweetTime
                post["MainTweet"]["LocationName"] = TweetLocation_name
                post["MainTweet"]["LocationLink"] = TweetLocation_link
                post["MainTweet"]["Device"] = TweetDevice
                post["MainTweet"]["Praise"] = TweetPraise
                post["MainTweet"]["RetweetTimes"] = TweetRetweet
                post["MainTweet"]["Comment"] = TweetComment
        #Tweet with pic.
        else:
            subTweetBranch = TweetBranch[0].xpath("./span[@class='ctt']")[0]
            TweetTheme,TweetAt = TweetThemeAtParser(subTweetBranch)                                             #Tweet Theme & At
            TweetContents = subTweetBranch.xpath("./text()")                                                         #Tweet content.
            TweetContent = ''
            for content in TweetContents:
                if content is not None and len(content)>0:
                    TweetContent = TweetContent + content.strip().replace(u'\xa0','')
            TweetLocation_name,TweetLocation_link = LocationParser(subTweetBranch,TweetContent)                 #Location name, location link.
            TweetPraise,TweetRetweet,TweetComment = TweetPraiseCommentRetweetParser(TweetBranch[1])             #Tweet praise,times,comment count.
            DevnTimeNode = TweetBranch[1].xpath("./span[@class='ct']")[0]                                       #Tweet time & Device that posts tweet.
            TweetTime,TweetDevice = DevicenTimeParser(DevnTimeNode)
            post["MainTweet"]["Content"] = TweetContent
            post["MainTweet"]["Theme"] = TweetTheme
            post["MainTweet"]["At"] = TweetAt
            post["MainTweet"]["Time"] = TweetTime
            post["MainTweet"]["LocationName"] = TweetLocation_name
            post["MainTweet"]["LocationLink"] = TweetLocation_link
            post["MainTweet"]["Device"] = TweetDevice
            post["MainTweet"]["Praise"] = TweetPraise
            post["MainTweet"]["RetweetTimes"] = TweetRetweet
            post["MainTweet"]["Comment"] = TweetComment
    #Retweet with pic.
    elif len(TweetBranch) == 3:
        #First div.
        subTweetBranch = TweetBranch[0].xpath("./span[@class='cmt']")
        RetTweetSource_Name = subTweetBranch[0].xpath("./a")[0].text                                        #Retweeted source info: nick name.
        RetTweetSource_Link,rubbish = subTweetBranch[0].xpath("./a")[0].attrib['href'].split('?')           #Retweeted source info: main page link.
        subTweetBranch = TweetBranch[0].xpath("./span[@class='ctt']")[0]
        RetTweetContents = subTweetBranch.xpath("./text()")                                                 #Retweeted content.
        RetTweetContent = ''
        for content in RetTweetContents:
            if content is not None and len(content)>0:
                RetTweetContent = RetTweetContent + content.strip().replace(u'\xa0','')                     #Tweet content.
        RetTweetTheme,RetTweetAt = TweetThemeAtParser(subTweetBranch)                                       #Retweeted Theme & At
        #Second div with retweeted info.
        RetTweetPraise,RetTweetTimes,RetTweetComment = TweetPraiseCommentRetweetParser(TweetBranch[1])      #Praise,times,comment count
        post["RetTweet"]["SourceName"] = RetTweetSource_Name
        post["RetTweet"]["SourceLink"] = RetTweetSource_Link
        post["RetTweet"]["Content"] = RetTweetContent
        post["RetTweet"]["Praise"] = RetTweetPraise
        post["RetTweet"]["RetweetTimes"] = RetTweetTimes
        post["RetTweet"]["Comment"] = RetTweetComment
        post["RetTweet"]["Theme"] = RetTweetTheme
        post["RetTweet"]["At"] = RetTweetAt
        #Third div with reason of retweet.
        TweetContents = TweetBranch[2].xpath("./text()")                                                    #Tweet content
        TweetContent = ''
        for content in TweetContents:
            if content is not None and len(content)>0:
                TweetContent = TweetContent + content.strip().replace(u'\xa0','')
        TweetTheme,TweetAt = TweetThemeAtParser(TweetBranch[2])                                             #Tweet Sharp & At
        TweetLocation_name,TweetLocation_link = LocationParser(TweetBranch[2],TweetContent)                 #Location name, location link.
        TweetPraise,TweetRetweet,TweetComment = TweetPraiseCommentRetweetParser(TweetBranch[2])             #Tweet praise,times,comment count.
        DevnTimeNode = TweetBranch[2].xpath("./span[@class='ct']")[0]                                       #Tweet time & Device that posts tweet.
        TweetTime,TweetDevice = DevicenTimeParser(DevnTimeNode)
        post["MainTweet"]["Content"] = TweetContent
        post["MainTweet"]["Theme"] = TweetTheme
        post["MainTweet"]["At"] = TweetAt
        post["MainTweet"]["Time"] = TweetTime
        post["MainTweet"]["LocationName"] = TweetLocation_name
        post["MainTweet"]["LocationLink"] = TweetLocation_link
        post["MainTweet"]["Device"] = TweetDevice
        post["MainTweet"]["Praise"] = TweetPraise
        post["MainTweet"]["RetweetTimes"] = TweetRetweet
        post["MainTweet"]["Comment"] = TweetComment
    #Defines data for return.

    data = json.dumps(post)
    return data


def TweetPraiseCommentRetweetParser(subTweetBranch):        #Tweet info parser.
    tags = subTweetBranch.xpath("./*")
    TweetInfo = {"PraiseCount":0,
                 "RetweetCount":0,
                 "CommentCount":0}
    count = 0
    for tag in tags:
        if count == 0 and tag.text:
            #PraiseCount = re.match(r'赞\[[0-9]+\]',tag.text)
            #if PraiseCount is not None:
            if re.match(u'赞\[[0-9]+\]',tag.text):
                TweetInfo["PraiseCount"] = re.search(r'[0-9]+',tag.text).group()
                count = count + 1
        elif count == 1 and tag.text:
            #RetweenCount = re.search(r'转发\[[0-9]+\]',tag.text)
            #if RetweenCount is not None:
            if re.search(u'转发\[[0-9]+\]',tag.text):
                TweetInfo["RetweetCount"] = re.search(r'[0-9]+',tag.text).group()
                count = count + 1
        elif count == 2 and tag.text:
            #CommentCount = re.search(r'评论\[[0-9]+\]',tag.text)
            #if CommentCount is not None:
            if re.search(u'评论\[[0-9]+\]',tag.text):
                TweetInfo["CommentCount"] = re.search(r'[0-9]+',tag.text).group()
                return TweetInfo["PraiseCount"],TweetInfo["RetweetCount"],TweetInfo["CommentCount"]
    return TweetInfo

def TweetThemeAtParser(subTweetBranch):
    Theme = []
    AT = []
    ATags = subTweetBranch.xpath("./a")
    if ATags is not None:
        for tag in ATags:
            tempTheme = re.search(r"#[\S]+#",tag.text)
            if tempTheme is not None:
                Theme.append(tempTheme.group())                                         #Theme
            if '@' in tag.text:
                ATnickname = tag.text.replace('@','')                                   #@
                ATlink = tag.attrib['href']
                AT.append([ATnickname,ATlink])
    return Theme,AT

def DevicenTimeParser(DevnTimeNode):
    DevnTime = DevnTimeNode.xpath("./text()")[0]
    if DevnTimeNode is None or len(DevnTime) == 0:
        return '',''
    posttime,postdevice = DevnTime.split(u'\xa0')
    #Deal with time.
    result_minutesago = re.search(u'[0-9]+分钟前',posttime)            #Within an hour.
    result_today = re.search(u'今天\s[0-9]*:[0-9]*',posttime)     #Within today.
    result_otherday = re.search(u'[0-9]*月[0-9]*日\s[0-9]*:[0-9]*',posttime)  #Within one year.
    result_otheryear = re.search(u'[0-9]+-[0-9]+-[0-9]+\s[0-9]+:[0-9]+:[0-9]+',posttime)  #Not this year.
    if result_minutesago:
        timegap = re.search(u'[0-9]+',posttime).group()
        posttime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()-int(timegap)*60))
    elif result_today:
        moment = re.search(u'[0-9]*:[0-9]*',posttime).group()
        daynow = time.strftime("%Y-%m-%d",time.localtime(time.time()))
        posttime = daynow + ' ' + moment
    elif result_otherday:
        posttime = result_otherday.group()
    elif result_otheryear:
        posttime = posttime
    #Deal with device.
    postdevice = postdevice.replace(u'来自','')
    if len(postdevice) == 0:
        postdevice = DevnTimeNode.xpath("./a/text()")[0]
    return posttime,postdevice

def LocationParser(subTweetBranch,TweetContent):
    TweetLocation_name = ''
    TweetLocation_link = ''
    if re.search(u'\[位置\]',TweetContent):
        subTweetNodes = subTweetBranch.xpath("./a")
        for node in subTweetNodes:
            try:
                url = node.attrib['href']
                if re.search(u"http://weibo.cn/sinaurl",url):
                    TweetLocation_link = url
                else:
                    TweetLocation_link = ''
                TweetLocation_name = node.text
                return TweetLocation_name,TweetLocation_link
            except KeyError:
                TweetLocation_name = ''
                TweetLocation_link = ''
    return TweetLocation_name,TweetLocation_link 

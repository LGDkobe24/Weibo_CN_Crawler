from Login import Fetcher
from Config import PreConfig

from lxml import etree
import lxml
import lxml.html.soupparser as sper
 
import re
import datetime
# -*- coding: utf-8 -*-
from pymongo import MongoClient

def UserFansDataInsert(data,fans_collection,candidate_collection,finished_collection,flag=False):
    for line in data:
        dataline = {
            'user_id':line[0],
            'fans_nickname':line[1],
            'fans_link':line[2],
            'fans_id':line[3]
            }
        fans_collection.insert(dataline)
        if flag:    #If true then start candidate insertion.
            if finished_collection.find_one({'finished_id':line[3]}) is None:
                candidate_collection.insert({'candidate_id':line[3]})


def UserFollowDataInsert(data,follow_collection,candidate_collection,finished_collection,flag=False):
    for line in data:
        dataline = {
            'user_id':line[0],
            'follower_nickname':line[1],
            'follower_link':line[2],
            'follower_id':line[3]
            }
        follow_collection.insert(dataline)
        if flag:    #If true then start candidate insertion.
            if finished_collection.find_one({'finished_id':line[3]}) is None:
                candidate_collection.insert({'candidate_id':line[3]})

def UserContentDataInsert(data,collection):
    for line in data:
        for subline in line:
            collection.insert(subline)

def starter(uid):
    PreConfiger = PreConfig()
    PreConfiger.LoginInfoSet()
    #DB config.
    client = MongoClient('localhost',27017)
    db = client['SinaTest']
    col_PreParser = db['PreParser']
    col_UserFans = db['UserFans']
    col_UserFollow = db['UserFollow']
    col_UserContent = db['UserContent']
    col_UserInfo = db['UserInfo']
    col_Candidate = db['Candidate']
    col_Finished = db['Finished']
    #Insert uid into candidate collection.
    if col_Finished.find_one({'finished_id':uid}) is None:
        temp_flag = True
        col_Candidate.insert({'candidate_id':uid})
    else:
        temp_flag = False
    while col_Candidate.find_one() is not None:
        if temp_flag == True:
            User_id = uid
            temp_flag = False
        else:
            User_id = col_Candidate.find_one()['candidate_id']
        if col_Finished.find_one({'finished_id':User_id}) is None:
            LogIner = Fetcher()
            username,password = PreConfiger.LoginInfoGet()      #Username, Password
            LogIner.login(username,password,'cookies.lwp',True,3.0)
            print "Dealing with: ",User_id, " ,with User name: ",username,", Password: ",password
            PreParserData = LogIner.UserPreParser(User_id)
            col_PreParser.insert(PreParserData)

            UserFansData = LogIner.UserFansPageParser(User_id)
            UserFansDataInsert(UserFansData,col_UserFans,col_Candidate,col_Finished,False)

            UserFollowData = LogIner.UserFollowPageParser(User_id)
            UserFollowDataInsert(UserFollowData,col_UserFollow,col_Candidate,col_Finished,False)

            UserContentData = LogIner.UserContentPageParser(User_id)
            UserContentDataInsert(UserContentData,col_UserContent)

            UserInfoData = LogIner.UserInfoParser(User_id)
            col_UserInfo.insert(UserInfoData)
            col_Candidate.remove({'candidate_id':User_id})
            col_Finished.insert({'finished_id':User_id})
            #Add follow user into candidate pool.
            UserFansDataInsert(UserFansData,col_UserFans,col_Candidate,col_Finished,True)
            UserFollowDataInsert(UserFollowData,col_UserFollow,col_Candidate,col_Finished,True)
        else:
            col_Candidate.remove({'candidate_id':User_id})


#PreConfiger = PreConfig()
#PreConfiger.LoginInfoSet()
#username,password = PreConfiger.LoginInfoGet()

uidInit = '5091182599'
starter(uidInit)
#client = MongoClient('localhost',27017)
#db = client['SinaTest']
#col_PreParser = db['PreParser']
#col_UserFans = db['UserFans']
#col_UserFollow = db['UserFollow']
#col_UserContent = db['UserContent']
#col_UserInfo = db['UserInfo']
#col_Candidate = db['Candidate']
#col_Finished = db['Finished']


#LogIner.login("smallyangy@163.com", "half0101155753", 'cookies.lwp')



#PreParserData = LogIner.UserPreParser(uidInit)
#col_PreParser.insert(PreParserData)

#UserFansData = LogIner.UserFansPageParser(uidInit)
#UserFansDataInsert(UserFansData,col_UserFans)

#UserFollowData = LogIner.UserFollowPageParser(uidInit)
#UserFollowDataInsert(UserFollowData,col_UserFollow)

#UserContentData = LogIner.UserContentPageParser(uidInit)
#UserContentDataInsert(UserContentData,col_UserContent)

#UserInfoData = LogIner.UserInfoParser('3700587630')
#col_UserInfo.insert(UserInfoData)

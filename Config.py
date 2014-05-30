import yaml
import sys
import os
#import random
import Queue

class PreConfig(object):
    def LoginInfoSet(self):
        if os.path.isfile('my.yaml'):
            absfile = os.path.abspath('my.yaml')
            abspath,filename = os.path.split(absfile)
            f = open(absfile,'r')
            self.dic_yaml = yaml.load(f)
            AccountCount = len(self.dic_yaml['job']['login'])/2
            #self.setRandomCount(AccountCount)
            #AccountSeq = self.getRandNum()
            self.setQueueNum(AccountCount)
        else:
            print "Cannot find file 'WeiboCN.yaml' in directory: ", abspath
    def LoginInfoGet(self):
        AccountSeq = self.getQueueNum()
        username = self.dic_yaml['job']['login'][AccountSeq*2]['username']
        password = self.dic_yaml['job']['login'][AccountSeq*2 + 1]['password']
        return username,password
    '''
    def setRandomCount(self,AccountCount):
        self.count = AccountCount
        self.randnum = self.count - 1    #Default start from the last.
        self.candidates = []
        for i in range(0,self.count):
            self.candidates.append(i)

    def getRandNum(self):
        temp = random.choice(self.candidates)
        while temp == self.randnum:
            temp = random.choice(self.candidates)
        self.randnum = temp
        return self.randnum
    '''
    def setQueueNum(self,AccountCount):
        self.AccountSerialQueue = Queue.Queue(maxsize=AccountCount)
        for i in range(0,AccountCount):
            self.AccountSerialQueue.put(i)

    def getQueueNum(self): #Can be implimented using __iter__.
        QueueLeader = self.AccountSerialQueue.get()
        self.AccountSerialQueue.put(QueueLeader)
        return QueueLeader
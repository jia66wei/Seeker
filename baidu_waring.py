#! /usr/bin/env python
#-*-encoding:utf8-*-
from httpClient import HttpClient
from json import JSONEncoder
'''
Created on 2016年7月5日

@author: wangheng
'''

class BaiduWaring():
    '''
    classdocs
    '''


    def __init__(self):
        
        '''
        Constructor
        '''
        self.servicekey = 'b81cadf0787225b996f79f05454722ac'
        self.service_id = '5713'
        self.event_type = 'trigger'
        
    def sendWaring(self,description):
        servicekey=self.servicekey
        service_id=self.service_id
        event_type=self.event_type
        headerDict={}
        headerDict['servicekey']=servicekey
        dataDict={}
        dataDict['service_id']=service_id
        dataDict['event_type']=event_type
        dataDict['description']=description
        url='http://gaojing.baidu.com/event/create'
        data=JSONEncoder().encode(dataDict)
        result=HttpClient().post(url,data, headerDict)
        return result
        
        
        
        
#! /usr/bin/env python
#-*-encoding:utf8-*-
'''
Created on 2016年6月23日

@author: wangheng
'''
import requests
# from data_server_common.common.single.singleton import Singleton
class HttpClient(object):
#     __metaclass__ = Singleton
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        
    def get(self,url,paramsDict=None):
        r = requests.get(url, data=paramsDict)
        return r.content
    
    def post(self,url,dataDict=None,headerDict=None,isProxies=False):
        if isProxies:
            proxies = {
                       "http": "http://10.131.30.18:8000",
                       "https": "http://10.131.30.18:8000",
                       }
            r = requests.post(url,data=dataDict,headers=headerDict,proxies=proxies)
        else:
            r = requests.post(url,data=dataDict,headers=headerDict)
        return r.content
    
# print HttpClient().postData("http://10.130.81.156:8103/feature",None,None)
# print HttpClient().post("http://gaojing.baidu.com/")
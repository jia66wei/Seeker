#-*-coding:utf8-*-

import os,sys,re
import time
import subprocess
import requests,cookielib
import getopt
import urllib2

from urllib import quote
from bs4 import BeautifulSoup
from lxml import etree  

reload(sys)
sys.setdefaultencoding("utf8")
code = 'utf8'

#session = requests.session()
#proxies = {'http':'http://10.131.16.74:8000', 'https': 'https://10.131.16.74:8000'}
#session.proxies = proxies

'''
	模拟登陆模块
	input：用户名密码验证码（模拟登录用）
	output：登录过的用户的uid列表文件，cookie信息文件
'''
class Login:
	def __init__(self):
		pass

	def loginStatus(self, response):
		soup = BeautifulSoup(response.text,"html.parser")
		if soup.find("div",{"class":"me"}) == None:
			print u"-----------登录成功---------"
		else:
			print u"-----------cookie已过期，重新登录！-----------"
			#self.loginSimulation()

	def loginStatus_s(self, response):
		soup = BeautifulSoup(response.text,"html.parser")
		if soup.find("div",{"class":"me"}) == None:
			print u"-----------登录成功---------".decode(code).encode('gbk')
			#print 'content ', response.content
			login_uid = re.findall(r'href=\"/([0-9]+)/info', response.content,re.I)
			login_uid = login_uid[0]
			cookieInfo = requests.utils.dict_from_cookiejar(session.cookies)
			cj = cookielib.LWPCookieJar('loginInfo_'+login_uid+'.txt')
			requests.utils.cookiejar_from_dict(cookieInfo, cj)
			cj.save('cookies/loginInfo_'+login_uid+'.txt', ignore_discard=True, ignore_expires=True)
			with open('login_users.txt', 'a') as f:		#存登录用户uid, 以便轮流登录
				f.write(login_uid+'\n')
			f.close()
		else:
			print u"-----------验证码或用户名或密码不对，请重新登录！-----------"
			self.loginSimulation()

	def loginWithCookies(self, cookie_uid,session):
		load_cj = cookielib.LWPCookieJar()
		cookie_uid = cookie_uid.replace('','')
		if os.path.exists(r'cookies/loginInfo_'+cookie_uid+'.txt') == False:
			print "This cookie does not exist!",cookie_uid
			self.loginSimulation()
			return
		load_cj.load('cookies/loginInfo_'+cookie_uid+'.txt', ignore_discard=True, ignore_expires=True)
		load_cookies = requests.utils.dict_from_cookiejar(load_cj)
		session.cookies = requests.utils.cookiejar_from_dict(load_cookies)
		param = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"}
		req = session.post("http://login.weibo.cn/login/?", headers=param)
		self.loginStatus(req)

	def loginSimulation(self):
		url = "http://login.weibo.cn/login/?"
		param = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"}
		CAPTCHAPath = os.path.join(os.getcwd(), 'CAPTCHA.jpg')
		username = raw_input(u"请输入用户名：")
		password = raw_input(u"请输入密码：")

		#username = 'ruixi93@gmail.com'
		#password = '01honey01lemon'
		#username = 'ruixi93@sina.com'
		#password = 'babyface011'
			
		req = requests.get(url, headers=param, proxies=proxies)
		req = requests.get(url, headers=param, proxies=proxies)
		soup = BeautifulSoup(req.text,"html.parser")
		img_url = soup.find("img").get("src")
		pass_name = soup.find("input",{"type":"password"}).get("name")
		backURL = soup.find("input",{"name":"backURL"}).get("value")
		backTitle = soup.find("input",{"name":"backTitle"}).get("value")
		vk = soup.find("input",{"name":"vk"}).get("value")
		capId = soup.find("input",{"name":"capId"}).get("value")
		submit = soup.find("input",{"name":"submit"}).get("value")
		
		r = requests.get(img_url, stream=True, proxies=proxies)
		if r.status_code == 200:
			with open(CAPTCHAPath, 'wb') as f:
				for chunk in r.iter_content(1024):
					f.write(chunk)
		time.sleep(1)
		if sys.platform.find('darwin') >= 0:
			subprocess.call(['open', CAPTCHAPath])
		elif sys.platform.find('linux') >= 0:
			subprocess.call(['xdg-open', CAPTCHAPath])
		else:
			os.startfile(CAPTCHAPath)
		CAPTCHA = raw_input(u"请输入验证码:".decode(code).encode('gbk'))		
		#data = {"mobile":username,pass_name:password,"code":quote(CAPTCHA.decode(code).encode("utf8")),"remember":"on","backURL":backURL,
		#"backTitle":backTitle,"vk":vk,"capId":capId,"submit":submit}
		#test git
		#for windows 
		data = {"mobile":username,pass_name:password,"code":quote(CAPTCHA.decode('gbk').encode("utf8")),"remember":"on","backURL":backURL,
		"backTitle":backTitle,"vk":vk,"capId":capId,"submit":submit}
		req = session.post("http://login.weibo.cn/login/?",data=data, headers=param)					
		self.loginStatus_s(req)

if __name__ == '__main__':
	login = Login()
	login.loginSimulation()

#-*-coding:utf8-*-

import os
import time, re
import random
from login import *
from account import *
from baidu_waring import *

class AccountDection():
	def __init__(self):
		self.session = requests.session()

	def accountflag(self, user):
		login = Login()
		login.loginWithCookies(user,self.session)

		url = 'http://weibo.cn/'+ user
		res = self.session.get(url)
		print "url: ", url

		cnt = 0
		while len(res.content) == 0 and cnt < 5:
			time.sleep(1)
			res = session.get(url)
			cnt += 1

		print res.content
		if len(res.content) == 0:
			flag = 2
		else:
			#content1 = re.findall(r"<span class=\"cmt\">加入新浪微博,(.*?)新鲜的事!</span>", res.content, re.I)    
			content1 = re.findall(r"\"/%s/follow\">关注\[[0-9]+\]"%user, res.content, re.I)  # the flag of login success...
			content2 = re.findall(r"location\.replace\(\"http\://weibo\.cn(.*?)\"\)\;", res.content, re.I) # update cookie info...
			print 'c1:',content1
			print 'c2:',content2
			if len(content1) > 0:
				flag = 0
			elif "抱歉，您的微博账号出现异常，暂时被冻结" in res.content:   #冻结
				flag = 1
			elif len(content2) > 0:
				flag = 3
			else:
				flag = 4

		return flag

	def checkaccount(self, user):
		flag = self.accountflag(user)
		print 'flag:',flag
		account = Account()
		username, password, nickname = account.find(user)
		if flag == 0:
			print nickname+'的账号'+'(ID为'+user+')正常'
			return
		if flag == 1:
			description = nickname+'的账号'+'(ID为'+user+')被封'
		elif flag == 2:
			description = nickname+'的账号'+'(ID为'+user+')异常'
		elif flag == 3:
			description = nickname+'的账号'+'(ID为'+user+')需要更新cookie'
		else:
			description = nickname+'的账号'+'(ID为'+user+')报错'

		bw = BaiduWaring()
		bw.sendWaring(str(description))

if __name__ == '__main__':

	with open('./user/uid_publishMblog.txt') as f:
		users = [l.strip() for l in f]

	#users = ['5779255287']

	test = AccountDection()
	while True:
		for i in xrange(0, len(users)):
			test.checkaccount(users[i])
			time.sleep(random.randint(20,100))
		if os.path.exists('./conf/stop.txt'):
			exit()

		time.sleep(3600)

#:-*-coding:utf8-*-
'''
@author:@jiawei
@date:20161009
@use:auto publish mblog...
'''

import sys
import logging
import random
import re 
import time
import urllib2
import urllib

from datetime import datetime
from multiprocessing import Process

from login import *
from mid_to_url import *


reload(sys)
sys.setdefaultencoding("utf8")

def getLog(logFile):
	'''
	log文件记录。。。
	'''
	r = logging.getLogger()
	r.setLevel(logging.WARNING)
	logger = logging.getLogger('mylogger')
	hdlr = logging.FileHandler(logFile)
	hdlr.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	logger.setLevel(logging.DEBUG)
	return logger

'''
	自动发博文模块
	-input: 待发博文内容
	-output: 博文发送状态（成功/失败）log文件
'''
class AutoPublish:
	def __init__(self, user):
		self.session = requests.session()
		self.login_user = user

		now = datetime.now()
		self.today = now.strftime('%Y%m%d')
		self.tool = ConversionTool()
		logging.basicConfig(level=logging.INFO,
			format='%(asctime)s %(filename)s %(levelname)s %(message)s',  
			datefmt='%a, %d %b %Y %H:%M:%S',  
			filename='log/mblog_publish_%s_'%(self.login_user)+self.today+'.log',
			filemode='a')
		self.logger = logging.getLogger()

	def IAmHuman(self):
		'''
		模拟人的正常行为,添加随机请求
		'''
		#login = Login()
		#login.loginWithCookies(user)

		behave = [
					'http://weibo.com/feed/hot?leftnav=1&page_id=102803_ctg1_1760_-_ctg1_1760', #热门微博
					'http://weibo.com/friends?leftnav=1&wvr=6&isfriends=1&step=2',#好友圈
					'http://weibo.com/fav?leftnav=1',#我的收藏
					'http://weibo.com/like/outbox?leftnav=1',#我的赞
					'http://d.weibo.com/102803_ctg1_6388_-_ctg1_6388#',#财经类热门微博
					'http://d.weibo.com/102803_ctg1_4388_-_ctg1_4388#',#搞笑类热门微博
					'http://s.weibo.com/top/summary?cate=realtimehot',#实时热搜榜
					'http://www.weibo.com/messages?topnav=1&wvr=6',#查看私信消息
					'http://www.weibo.com/comment/inbox?topnav=1&wvr=6&f=1',#查看评论消息
					'http://www.weibo.com/like/inbox?topnav=1&wvr=6&f=1',#查看赞消息
					'http://www.weibo.com/',#查看微博主页
					'http://d.weibo.com/100803?refer=index_hot_new',#查看热门话题
				]
		#随机选取nums个行为进行模拟
		nums = 5
		child_bhv = random.sample(behave,nums)
		for bhv in child_bhv :
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
			}	
			headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"}
			res = self.session.get(bhv, headers=headers)

			#尽可能不规律
			rand = random.randint(1,10)
			if rand % 4 == 0:
				time.sleep(random.randint(50,100))			
			else:
				time.sleep(random.randint(30,70))			

	def repostPublish(self, post_comment, shorturl, st):
		'''
			模拟发送一条博文内容：填写表单信息，发post request，记录发送情况log
		'''
	
		#url = 'http://weibo.cn/comments/addcomment?st='+st
		url = 'http://weibo.cn/mblog/sendmblog?st='+st	
		url = 'http://weibo.cn/repost/dort/%s?gid=10001&st=%s'%(shorturl,st)
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
		}	
		headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"}
		form_data = {
				'act':'dort',
				'rl': '1',
				'id': shorturl,
				'rtkeepreason': 'on',
				'content': post_comment
		}
		res = self.session.post(url, data=form_data, headers=headers)
		#记录哪些SUCCESS, 哪些FAIL
		content = res.content
		print 'content:',content
		return 'editsuccess'

	def postPublish(self, post_comment, st):
		'''
			模拟发送一条博文内容：填写表单信息，发post request，记录发送情况log
		'''
	
		#url = 'http://weibo.cn/comments/addcomment?st='+st
		url = 'http://weibo.cn/mblog/sendmblog?st='+st	
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
		}	
		headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"}
		form_data = {
			'rl': '0',
			'content': post_comment
		}
		res = self.session.post(url, data=form_data, headers=headers)
		#记录哪些SUCCESS, 哪些FAIL
		content = res.content
		print 'content:',content
		return 'editsuccess'

	def create(self,f_mblog, st1, start_page=0):
		'''
		   1.输入mblog列表文件名和起始页码，遍历mblog列表，每条mblog call postPublish模块发博文，返回博文发送状态
		   2.博文内容从f_mblog文件顺序选出
		'''
		with open(f_mblog) as f:
			contents = f.readlines()
		f.close()

		for num in range(start_page, len(contents)):
			line = contents[num]
			line = line.rstrip('\n').split('\t')
			mblog_content = line[1] 
			shorturl = line[0]	
			edit_status = self.repostPublish(mblog_content,shorturl,st1)
			#add by @jiawei
			#sleep_time = random.randint(3600,20000)
			sleep_time = 2
			self.logger.info("publish mblog:%s-sleep_time:%s"%(mblog_content,sleep_time))
			#time.sleep(sleep_time) #避免因update weibo too fast, account or ip or app is illegal造成的评论失败
			#self.IAmHuman()
		return 'editsuccess'

	def publishProcess(self, user,ad):
		login = Login()
		start_page = 0  #start publish  line
		login.loginWithCookies(user,self.session)
		url = 'http://weibo.cn/'+user+'/profile'	#登录者主页源代码里有st值信息
		res = self.session.get(url)
		st = re.findall(r';st=(.+?)\"', res.content, re.I)
		st1 = st[0]
		print 'start_page', start_page
		flag = self.create(ad, st1, start_page)

def Publish(user, ad):
	print 'user:',user
	publisher = AutoPublish(user)
	publisher.publishProcess(user, ad)
		
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "need 'exe','userfile','mblogfile'"
		exit()
	# 多进程，多个账号同时登录发送评论
	# read in cookie users
	fn1 = sys.argv[1]
	mblog = sys.argv[2]
	with open(fn1) as f:
		users = f.readlines()
	f.close()

	num_users = len(users)
	#multiprocessing
	count = 0
	plist = []
	for i in xrange(num_users):
		count += 1
		p = Process(target = Publish, args = (users[i].rstrip('\n'), mblog,))
		plist.append(p)
		p.start()
		seconds = random.randint(5,80)
		time.sleep(seconds) 
		print 'sleep %s seconds...'%seconds
		if count%num_users == 0:
			for p in plist:
				p.join()	#要求主进程等待子进程运行完毕
		plist = []
		#break
	if len(plist)>0:
		for p in plist:
			p.join()

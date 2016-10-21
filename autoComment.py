#:-*-coding:utf8-*-
'''
@author:ruixilin
@updated:@jiawei
@date:20160919
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

RE_link = re.compile(ur'http.*[a-zA-Z]')

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
	自动评论模块
	-input: mid文件路径，广告语文件路径（以后可按需优化）
	-output: 评论发送状态（成功/失败）log文件
'''
class AutoComment:
	def __init__(self, user):
		self.session = requests.session()
		self.login_user = user

		now = datetime.now()
		self.today = now.strftime('%Y%m%d')
		self.tool = ConversionTool()
		logging.basicConfig(level=logging.INFO,
			format='%(asctime)s %(filename)s %(levelname)s %(message)s',  
			datefmt='%a, %d %b %Y %H:%M:%S',  
			filename='log/publish_%s_'%(self.login_user)+self.today+'.log',
			filemode='a')
		self.logger = logging.getLogger()
		'''
		filename='log/publish_%s_'%(self.login_user)+self.today+'.log',
		self.logger = getLog(filename)
		'''

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
			res = self.session.get(bhv, headers=headers)

			#尽可能不规律
			rand = random.randint(1,10)
			if rand % 4 == 0:
				time.sleep(random.randint(40,150))			
			else:
				time.sleep(random.randint(30,70))			

	def check_publish(self,userid,mid):
		'''
		监测下发布的评论是否落地到用户主页下面
		'''
		url = 'http://weibo.cn/comment/'+ mid
		res = self.session.get(url)
		print "url: ", url

		cnt = 0
		while len(res.content) == 0 and cnt < 5:
			time.sleep(random.randint(10,60))
			res = self.session.get(url)
			cnt += 1

		if len(res.content) == 0:
			print "~~~~~~~~~~~~~~~~~~~~~~~spider fail~~~~~~~~~~~~~~~~~~~~~~~"
			return
		else:
			text = re.sub(' ', '', res.content)
			contents = re.findall(r"\"评论并转发\"name=\"rt\"/></div>(.*?)</span></div><div", text, re.I)
			content = re.findall(r"class=\"s\"></div>(.*?)</span></div><div", text, re.I)
			for i in range(1, len(content)):
				contents.append(content[i])
	
		cdict = {}
		flag = 0
		comment = 'NULL'
		for x in contents:
			uid = re.findall(r"fuid=(.*?)&amp;", x, re.I)
			if "<spanclass=\"ctt\">回复<ahref=" in str(x):
				ctype = 1
				comment = re.findall(r"<spanclass=\"ctt\">(.*?)</span>", x, re.I)
				comment = re.sub('回复<ahref=\"(.*?)>|</a>|:', '', comment[0])
			else:
				ctype = 0
				comment = re.findall(r"<spanclass=\"ctt\">(.*?)</span>", x, re.I)
				comment = comment[0]

			comment = re.sub('<ahref=\"(.*?)>|</a>|:', '', comment)
			dt = re.findall(r"<spanclass=\"ct\">(.*?)&nbsp;", x, re.I)

			text = str(mid)+'\t'+str(uid[0])+'\t'+str(ctype)+'\t'+str(comment).encode("utf8")+'\t'+str(dt[0])+'\n'

			cdict[uid[0]] = text
			if uid[0] in userid:
				flag = 1

		if flag != 0:
			self.logger.info("%s\t%s\t%s\t%s"%(mid,userid,str(comment),'check_pubSuccess'))
		else:
			self.logger.info("%s\t%s\t%s\t%s"%(mid,userid,str(comment),'check_pubFailed'))


	def postComment(self,postuser, uid, mid, post_comment, st):
		'''
		模拟发送一条评论：填写表单信息，发post request，记录发送情况log
		'''
	
		#short_url = self.tool.mid_to_url(int(mid))	# mid转短链
		short_url = mid
		print "short_url", short_url
		url = 'http://weibo.cn/comments/addcomment?st='+st
		#url = 'http://weibo.cn/comments/addcomment?st=6e123d'	# fake st
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
		}	
		form_data = {
			'srcuid': uid,
			'id': short_url,
			'rl': '1',
			'content': post_comment
		}
		res = self.session.post(url, data=form_data, headers=headers)
		#记录哪些SUCCESS, 哪些FAIL
		content = res.content
		if content.find('评论失败') != -1:
			details = re.findall(r'评论失败(.+?)<', content, re.I)
			#记录评论失败原因
			print details[0]
			flag = 'FAILURE cannot comment'+details[0]
		elif content.find('操作失败') != -1:
			flag = 'FAILURE post request fails'		#如果某次操作失败，意味着之后的操作也会失败，所以返回main函数，换账号登录
			print "flag1 ", flag
			return 'editfailure'
		else:
			flag = 'SUCCESS'
		self.logger.info("%s\t%s\t%s\t%s"%(mid,uid,post_comment,flag))

		#add by jiawei @20160919
		self.check_publish(postuser,mid)
		return 'editsuccess'

	def comment(self,postuser,filename, f_comment, st1, start_page=0):
		'''
		   1.输入mid列表文件名和起始页码，遍历mid列表，每条mid call postComment模块发评论，返回评论发送状态
		   2.评论内容从f_comment文件随机选出
		'''
		flag  = 1 #发送方式
		if f_comment == 'no_file_fanyi':
			flag =  4
		elif f_comment == 'no_file_ice':
			flag = 3 
		else:
			with open(f_comment) as f:
				comment_contents = f.readlines()
			f.close()

		with open(filename) as f:
			mids = f.readlines()
		f.close()
		
		channel_name = os.path.basename(f_comment).split('.')[0]
		for num in range(start_page, len(mids)):
			line = mids[num]
			line = line.strip('\n').split('\t')
			uid = line[0]
			if flag != 1:
				mid = line[1]
				######################################################
				comment_content = line[flag]  #记得更改, 小冰-3;fanyi-4
				#######################################################
			else:
				mid = line[3]
				comment_content = comment_contents[random.randint(0, len(comment_contents)-1)]
			edit_status = self.postComment(postuser,uid, mid, comment_content, st1)
			if edit_status == 'editfailure':
				status = ['editfailure', num]
				return status
			#add by @jiawei
			self.logger.info("line-num:%s\t%s\t%s"%(str(num),mid,uid))
			if num % 50 == 0 :
				time.sleep(random.randint(1800,3600)) #发送50条后进行休息。。。
			else:
				time.sleep(random.randint(60,80)) #避免因update weibo too fast, account or ip or app is illegal造成的评论失败
			self.IAmHuman()
		return 'editsuccess'

	def commentProcess(self, user, fn2,ad):
		login = Login()
		start_page = 0
		login.loginWithCookies(user,self.session)
		url = 'http://weibo.cn/'+user+'/profile'	#登录者主页源代码里有st值信息
		res = self.session.get(url)
		st = re.findall(r';st=(.+?)\"', res.content, re.I)
		st1 = st[0]
		print 'st:',st1
		print 'start_page', start_page
		flag = self.comment(user, fn2, ad, st1, start_page)
		if flag[0] == 'editfailure':
			print "该账号发送评论过于频繁，已被禁！转到下一账号".encode('gbk', 'ignore')

def Publish(user, fn2,ad):
	commenter = AutoComment(user)
	commenter.commentProcess(user, fn2,ad)
		
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "need 'exe','file'"
		exit()
	# 多进程，多个账号同时登录发送评论
	# read in cookie users
	fn1 = sys.argv[1]
	fn2 = sys.argv[2]
	ad = sys.argv[3]
	with open(fn1) as f:
		users = f.readlines()
	f.close()
	# read in mid file
	with open(fn2) as f:
		lines = f.readlines()
	f.close()

	num_users = len(users)
	mids = []
	fout = []

	for i in xrange(num_users):
		out_name = fn2.split('.')[0]+'_'+str(i)+'.txt'
		mids.append(out_name)
		fout.append(open(out_name,'w'))	
	for i in xrange(len(lines)):
		mod =  i % num_users
		fout[mod].write(lines[i])
	for i in xrange(num_users):
		fout[i].close()

	# multiprocessing
	count = 0
	plist = []
	for i in xrange(num_users):
		count += 1
		p = Process(target = Publish, args = (users[i].rstrip('\n'), mids[i],ad,))
		plist.append(p)
		p.start()
		seconds = random.randint(5,80)
		time.sleep(seconds)
		print 'sleep %s seconds...'%seconds
		if count%3 == 0:
			for p in plist:
				p.join()	#要求主进程等待子进程运行完毕
		plist = []
		#break
	if len(plist)>0:
		for p in plist:
			p.join()

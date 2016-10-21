#:-*-coding:utf8-*-

import urllib2
import urllib
import time, math
import sys
from login import *
import logging
import random
from datetime import datetime
from mid_to_url import *
from multiprocessing import Process
import re 

RE_link = re.compile(ur'http.*[a-zA-Z]')


reload(sys)
sys.setdefaultencoding("utf8")
'''
	自动评论模块
	-input: mid文件路径，广告语文件路径（以后可按需优化）
	-output: 评论发送状态（成功/失败）log文件
'''
class AutoComment:
	def __init__(self, user):
		self.login_user = user
		now = datetime.now()
		self.today = now.strftime('%Y%m%d')
		self.tool = ConversionTool()
		logging.basicConfig(level=logging.INFO,
			format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
			datefmt='%a, %d %b %Y %H:%M:%S',  
			filename='log/publish_%s_'%(self.login_user)+self.today+'.log',
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
			res = session.get(bhv, headers=headers)
			print bhv
			#print 'res.content:',res.content
			time.sleep(random.randint(3,5))			

	def postComment(self, uid, mid, post_comment, st):
		'''
		模拟发送一条评论：填写表单信息，发post request，记录发送情况log
		'''
	
		#short_url = self.tool.mid_to_url(int(mid))	# mid转短链
		print uid,mid,post_comment,st
		url = 'http://weibo.cn/comments/addcomment?st='+st
		#url = 'http://weibo.cn/comments/addcomment?st=6e123d'	# fake st
		headers = {
			#'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:48.0) Gecko/20100101 Firefox/48.0'
		}	
		form_data = {
			'srcuid': uid,
			'id': mid,
			'rl': '1',
			'content': post_comment
		}
		print form_data
		res = session.post(url, data=form_data, headers=headers)
		#记录哪些SUCCESS, 哪些FAIL
		content = res.content
		#print content
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
		print "flag ", flag
		self.logger.info("%s\t%s\t%s\t%s"%(mid,uid,post_comment,flag))
		return 'editsuccess'

	def comment(self, lines, st1, start_page=0):
		'''
		输入mid列表文件名和起始页码，遍历mid列表，每条mid call postComment模块发评论，返回评论发送状态
		'''
		for num in range(start_page, len(lines)):
			line = lines[num].strip('\n').split('\t')
			mid = line[1]
			uid = line[0]
			comment_content = line[4]
			'''
			comment_index = random.randint(0, len(comment_contents)-1)
			comment_content = comment_contents[comment_index]
			'''
			print mid, uid
			print "comment_content: ",comment_content

			#print 'comment content: ', comment_content.encode('gbk', 'ignore')
			edit_status = self.postComment(uid, mid, comment_content, st1)
			if edit_status == 'editfailure':
				status = ['editfailure', num]
				return status
			self.IAmHuman()
			time.sleep(random.randint(60,120)) #避免因update weibo too fast, account or ip or app is illegal造成的评论失败
		return 'editsuccess'

	def commentProcess(self, user, mids):
		login = Login()
		login.loginWithCookies(user)
		st = self.getst(user)
		flag = self.comment(mids, st)

		if flag[0] == 'editfailure':
			print "该账号发送评论过于频繁，已被禁！转到下一账号".encode('gbk', 'ignore')

	def getst(self, user):
		url = 'http://weibo.cn/'+user+'/profile'	#登录者主页源代码里有st值信息
		print url
		res = session.get(url)
		#print res.content
		st = re.findall(r';st=(.+?)\"', res.content, re.I)

		return st[0]
		#return '8129a5'
		
if __name__ == '__main__':

	# 多进程，多个账号同时登录发送评论
	#commenter = AutoComment()
	# read in cookie users

	with open('user/uid_fanyi.txt') as f:
		users = f.readlines()

	with open('./data/active_tweets_uniq_uidac_fanyi') as f:
		lines = f.readlines()

	line = []
	for i in range(len(lines)):
		line.append(lines[i])

	num_users = len(users)
	num_lines = len(line)
	print "num_users:", num_users
	print "num_lines:", num_lines

	# multiprocessing
	count = 0
	plist = []
	data_offset_start = 0
	data_split_count = int(math.ceil(float(num_lines)/num_users))
	
	for i in xrange(num_users):
		count += 1
		commenter = AutoComment(users[i]) 
		p = Process(target = commenter.commentProcess, args = (users[i].strip('\n'), line[data_offset_start:data_offset_start+data_split_count],))
		data_offset_start += data_split_count
		#p = Process(target = commenter.commentProcess, args = (users[i].strip('\n'), mids[i],))
		plist.append(p)
		p.start()
		if count%num_users == 0:
			for p in plist:
				p.join()	#要求主进程等待子进程运行完毕
		plist = []
		#break
	if len(plist)>0:
		for p in plist:
			p.join()
	plist = []


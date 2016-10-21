#:-*-coding:utf8-*-
'''
@author:ruixilin
'''

import urllib2
import urllib
import time
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
			filename='log/publish_chujie13818_%s_'%(self.login_user)+self.today+'.log',
			filemode='a')
		self.logger = logging.getLogger()

	def timeFormat(self):
		return time.strftime('%Y%m%d',time.localtime(time.time()))

	def postComment(self, uid, mid, post_comment, st):
		'''
		模拟发送一条评论：填写表单信息，发post request，记录发送情况log
		'''
	
		short_url = self.tool.mid_to_url(int(mid))	# mid转短链
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
		res = session.post(url, data=form_data, headers=headers)
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
		print "flag ", flag
		self.logger.info("%s\t%s\t%s\t%s"%(mid,uid,post_comment,flag))
		return 'editsuccess'

	def comment(self, filename, f_comment, st1, start_page=0):
		'''
		输入mid列表文件名和起始页码，遍历mid列表，每条mid call postComment模块发评论，返回评论发送状态
		'''
		# get post query parameter st using API (not applied)
		#url = 'https://api.weibo.com/2/users/show.json?access_token=2.00DyZUyBv5KO5D94bb09a464TFSZWB&screen_name='+login_user
		#res = session.get(url)
		#login_uid = re.findall(r'\"id\":(.+?),', res.content, re.I)
		#print 'login_uid ', login_uid[0]
		with open(f_comment) as f:
			comment_contents = f.readlines()
		f.close()
		with open(filename) as f:
			mids = f.readlines()
		f.close()
		channel_name = os.path.basename(f_comment).split('.')[0]
		for num in range(start_page, len(mids)):
			print "page: ", num
			line = mids[num]
			line = line.strip('\n').split()
			mid = line[0]
			uid = line[1].split('/')[-1]
			print mid, uid
			# random一条广告语料库ad.txt里的广告语
			dt = self.timeFormat()
			comment_index = random.randint(0, len(comment_contents)-1)
			link_info = RE_link.findall(comment_contents[comment_index])[0] +"&utm_term=seeker-%s-%s"%(channel_name,str(comment_index)) + "&utm_content=%s"%dt
			comment_content = RE_link.sub(link_info,comment_contents[comment_index])
			#comment_content = comment_contents[random.randint(0, len(comment_contents)-1)]
			#print 'comment content[0]: ', comment_content.encode('gbk', 'ignore').split()[0]
			#print 'comment content[1]: ', comment_content.encode('gbk', 'ignore').split()[1]

			edit_status = self.postComment(uid, mid, comment_content.split()[1], st1)
			if edit_status == 'editfailure':
				status = ['editfailure', num]
				return status
			time.sleep(random.randint(30,60)) #避免因update weibo too fast, account or ip or app is illegal造成的评论失败
			edit_status = self.postComment(uid, mid, comment_content.split()[0], st1)
			if edit_status == 'editfailure':
				status = ['editfailure', num]
				return status
			time.sleep(random.randint(30,60))
		return 'editsuccess'

	def commentProcess(self, user, fn2):
		login = Login()
		#使用cookie登录，press c; else press l
		'''
		user_input = ''
		while user_input not in ['s','S','c','C']:
			user_input = raw_input(u"使用cookie登录，请按c; 使用用户名密码登录，请按s： ".decode(code).encode('gbk'))
		if user_input in ['s','S']:
			login.loginSimulation()
		elif len(os.listdir('cookies')) == 0:
			print "Empty folder!"
			login.loginSimulation()
		'''
		start_page = 0
		login.loginWithCookies(user)
		url = 'http://weibo.cn/'+user+'/profile'	#登录者主页源代码里有st值信息
		res = session.get(url)
		#print res.content.encode('gbk','ignore')
		st = re.findall(r';st=(.+?)\"', res.content, re.I)
		st1 = st[0]
		#print st1
		print 'start_page', start_page
		flag = self.comment(fn2, 'ad_chujie_1.txt', st1, start_page)
		#flag = self.comment(fn2, 'ad.txt', st1, start_page)
		if flag[0] == 'editfailure':
			print "该账号发送评论过于频繁，已被禁！转到下一账号".encode('gbk', 'ignore')

def test(user, fn2):
	commenter = AutoComment(user)
	commenter.commentProcess(user, fn2)
		
if __name__ == '__main__':

	# 多进程，多个账号同时登录发送评论
	#commenter = AutoComment()
	# read in cookie users
	#with open('login_users_1.txt') as f:
	with open('uid_test.txt') as f:
		users = f.readlines()
	f.close()
	# read in mid file
	fn2 = '20160726test/mids_chujie_20160726_wap.txt'
	while not os.path.exists(fn2):
		fn2 = raw_input('请输入mid列表文件路径： '.encode('gbk', 'ignore'))
	# split mid file into smaller files by the number of users(processes)
	with open(fn2) as f:
		lines = f.readlines()
	f.close()
	num_users = len(users)
	mids = []
	for i in xrange(len(lines)):
		out_name = fn2.split('.')[0]+'_'+str(i%num_users)+'.txt'
		#print out_name
		if out_name not in mids:
			mids.append(out_name)
		with open(out_name, 'a') as fout:
			fout.write(lines[i])
		fout.close()
	# multiprocessing
	count = 0
	plist = []
	for i in xrange(num_users):
		count += 1
		p = Process(target = test, args = (users[i].strip('\n'), mids[i],))
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
	'''
	# 单进程
	login = Login()
	#使用cookie登录，press c; else press l
	user_input = ''
	while user_input not in ['s','S','c','C']:
		user_input = raw_input(u"使用cookie登录，请按c; 使用用户名密码登录，请按s： ".decode(code).encode('gbk'))
	if user_input in ['s','S']:
		login.loginSimulation()
	elif len(os.listdir('cookies')) == 0:
		print "Empty folder!"
		login.loginSimulation()
	with open('login_users_2.txt') as f:
		start_page = 0
		for user in f.readlines():
			user = user.strip('\n')
			login.loginWithCookies(user)
			url = 'http://weibo.cn/'+user+'/profile'	#登录者主页源代码里有st值信息
			res = session.get(url)
			#print res.content.encode('gbk','ignore')
			st = re.findall(r';st=(.+?)\"', res.content, re.I)
			st1 = st[0]
			#print st1
			#st1 = ' fd69fe'
			commenter = AutoComment(user)
			fn2 = ''
			while not os.path.exists(fn2):
				fn2 = raw_input('请输入mid列表文件路径： '.encode('gbk', 'ignore'))
			print 'start_page', start_page
			flag = commenter.comment(fn2, 'ad_chujie_1.txt', st1, start_page)
			if flag[0] == 'editfailure':
				print "该账号发送评论过于频繁，已被禁！转到下一账号".encode('gbk', 'ignore')	#还需要返回从mid文件的哪几行开始爬，重新登录后从这里开始爬
				start_page = flag[1]
				continue
			else:
				break
	f.close()
	'''

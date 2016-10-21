#-*-coding:utf8-*-

from login import *
from datetime import datetime
import os
from multiprocessing import Process

'''
	爬取热门博文评论者uid模块
	- input: TODO
	- output: TODO
'''
class HotTweet():
	def __init__(self):
		now = datetime.now()
		self.today = now.strftime('%Y%m%d')

	'''
		使用评论接口爬取由getHotTweets函数获取的热门博文的评论列表前20页的评论者uid
	'''	
	def getCommenters(self, mid, filename):
		print "mid: ", mid
		count = 100
		#numComments = int(numComments)
		#print "numComments: ", numComments
		#limit =  numComments/count+1 if numComments>count else 2
		#if limit>11:
		#	limit = 11
		#print "limit: ", limit
		mergedList = []
		limit = 20
		for page in range(1, limit):
			time.sleep(2)
			print "page", page
			#url = 'https://api.weibo.com/2/comments/show.json?access_token=2.00PopvFG0hVzju598230862b019v9P&id=%s&count=%s&page=%s' % (mid, count, page)
			#url = 'https://api.weibo.com/2/comments/show.json?access_token=2.001MgSFDXyliKDe735458d026N3rPE&id=%s&count=%s&page=%s' % (mid, count, page)
			url = 'https://api.weibo.com/2/comments/show.json?access_token=2.00DyZUyBv5KO5D94bb09a464TFSZWB&id=%s&count=%s&page=%s' % (mid, count, page)
			req = session.get(url)
			res = req.content
			print "page content: ", res
			if 'created_at' not in res:
				break
			comment_ids = re.findall(r"\"user\"\:{\"id\":([0-9]+),\"idstr\"", res, re.I)
			#print "commenter uids: ",comment_ids
			if len(comment_ids) > 0:
				items = dict([(comment_ids.count(i), i) for i in comment_ids])			# 去掉原博id(出现次数最多的id)
				ori_id = items[max(items.keys())]
				comment_ids = list(set(comment_ids))
				comment_ids.remove(ori_id)
				mergedList += comment_ids
		print 'len mergedList ',len(mergedList)
		with open(filename, "a") as f:
			for k in mergedList:
				f.write('http://www.weibo.com/u/'+k+'\n')
		f.close()

	'''
		爬取分类热门微博第一页的所有博文的mid
	'''
	def getHotTweets(self, url, filename):
		res = session.get(url)
		tweetList = re.findall(r"&mid=([0-9]+)&name", res.content, re.I)
		print "number of tweets in this page: ", len(tweetList)
		for i in range(len(tweetList)):
			self.getCommenters(tweetList[i], filename)


	'''
		不使用评论接口爬取分类热门微博前50页所有博文的评论者uid
	'''
	def crawlCommenters(self, url, filename,user):
		for i in range(1, 50):
			time.sleep(1)
			print "page ", i
			url = url+'&page=%s' % i
			res = session.get(url)
			#print "res: ", res.content
			shortLinks = re.findall(r"<div class=\"c\" id=\"M_(.+?)\">", res.content, re.I)	#获取每页的所有博文短链
			#print "short ", shortLinks
			shortLinks = list(set(shortLinks))
			for link in shortLinks:
				with open('mids/mid_remen_%s_%s_licai_.txt'%(self.today, user),'a') as fn:
					fn.write('http://weibo.cn/comment/'+link+'\n')
				fn.close()
				turl = 'http://weibo.cn/comment/'+link
				print "turl ", turl
				res = session.get(turl)
				numPage = re.findall(r"&nbsp;1/([0-9]+)页", res.content, re.I)
				pages = 1 if len(numPage) == 0 else int(numPage[0])
				print 'number of pages in comment list ', pages
				for page_num in range(1, pages+1):
					turl = 'http://weibo.cn/comment/'+link+'?page=%s' % page_num
					res = session.get(turl)
					commenters = re.findall(r"<a href=\"\/u\/(.+?)\">", res.content, re.I)
					commenters = list(set(commenters))
					for commenter in commenters:
						with open(filename, 'a') as f:
							f.write('http://www.weibo.com/u/'+commenter+'\n')
						f.close()

	'''
		文件去重
		-Input: 存下来的uid文件
		-Output：去重后的uid文件
	'''
	def removeDuplicates(self, fout):
		with open(fout) as f:
			commenters = f.readlines()
			print 'before: ', len(commenters)
			commenters = list(set(commenters))
			print 'after: ', len(commenters)
		f.close()
		fout = 'commenters/commenters_'+self.today+'_nodup.txt'
		with open(fout, 'a') as f:
			for c in commenters:
				f.write(c)
		f.close()
		return fout

	def getCommentersProcess(self, user, url):
		login = Login()
		login.loginWithCookies(user)
		fout = 'commenters/commenters_%s_licai_'%(user)+self.today+'.txt'		# 大写Y：2016 小写y: 16
		self.crawlCommenters(url, fout, user)

def test(user, url):
	crawler = HotTweet()
	crawler.getCommentersProcess(user, url)
	

if __name__ == '__main__':
	# read in cookie users
	with open('login_users_1.txt') as f:
		users = f.readlines()
	f.close()
	# read in urls
	with open('urls_by_categories.txt') as fp:		# 分类热门博文链接
		urls = fp.readlines()
	fp.close()
	# multiprocessing
	count = 0
	plist = []
	num_users = len(users)
	for i in xrange(num_users):
		count += 1
		p = Process(target = test, args = (users[i].strip('\n'), urls[i].strip('\n').split()[0],))
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
	login = Login()
	#使用cookie登录，press c; else press l
	user_input = raw_input(u"使用cookie登录，请按c; 使用用户名密码登录，请按s： ".decode(code).encode('gbk'))
	while user_input not in ['s','S','c','C']:
		user_input = raw_input(u"使用cookie登录，请按c; 使用用户名密码登录，请按s： ".decode(code).encode('gbk'))
	print "user input ", user_input
	if user_input in ['s','S']:
		login.loginSimulation()
	elif len(os.listdir('cookies')) == 0:
		print "Empty folder!"
		login.loginSimulation()
	with open('login_users.txt') as f:
		for user in f.readlines():
			user = user.strip('\n')
			login.loginWithCookies(user)
			now = datetime.now()
			today = now.strftime('%Y%m%d')
			fout = 'commenters/commenters_'+today+'.txt'		# 大写Y：2016 小写y: 16
			hotTweet = HotTweet()
			with open('urls_by_keywords.txt') as fp:		# 获取评论者uid
				for line in fp.readlines():
					url = line.strip('\n').split()[0]
					print url
					hotTweet.crawlCommenters(url, fout)
			fp.close()
			# TODO: 若断开，重新登录，重新爬（不管重复的），之后再去重 断开的条件？？？
			#if flag=='editfailure':
			#		print "该账号发送评论过于频繁，已被禁！转到下一账号".encode('gbk', 'ignore')
			#		continue
			#	else:
			#		break
			break
	f.close()
	hotTweet.removeDuplicates(fout)
	'''


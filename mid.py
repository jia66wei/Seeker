#-*-coding:utf8-*-
from login import *
from datetime import datetime
from mid_to_url import *
from datetime import datetime
from multiprocessing import Process
import random

'''
	1.用户主页最新博文mid获取(getMids+getFirstTwoMids)
	-input: 用户主页url列表文件
	-output: 用户主页最新博文mid列表文件
	2.找和理财相关的最新一条微博-->直接找关键词搜索出来的最新微博
	-input: 关键词
	-output: 含关键词的实时微博的mid列表文件
'''
class Mid():
	def __init__(self):
		now = datetime.now()
		self.today = now.strftime('%Y%m%d')
		ctool = ConversionTool()
		self.tool = ctool

	'''
		input: 用户主页链接, 要存的mid文件名
		output: 最新两条mid
	'''
	def getFirstTwoMids(self, fanUrl, filename2):
		url = fanUrl+"?profile_ftype=1&is_all=1"
		#print "url: ", url
		req = session.get(url)
		res = req.content
		#print "res", res
		mids = re.findall(r"&mid=([0-9]+)&name", res, re.I)
		print "number of tweets shown on homepage: ", len(mids)
		if len(mids) < 2:
			return
		#print mids[0], mids[1]
		with open(filename2, 'a') as f:
			f.write(mids[0]+' '+fanUrl+'\n')
			f.write(mids[1]+' '+fanUrl+'\n')
		f.close()

	'''
		input: uid文件名，要存的mid文件名
		output: mid列表文件
	'''	
	def getMids(self, filename1, filename2):
		fansList = [line.strip('\n').split()[0] for line in open(filename1)]
		fansList = list(set(fansList))
		#print "fansList ", fansList
		for j in range(len(fansList)):
			print "current fan: ", j
			self.getFirstTwoMids(fansList[j], filename2)
			time.sleep(random.randint(10,20))

	def getMidByKeyword(self):
		'''
			搜索含关键词的实时微博
			input: 关键词
			output: mid列表文件
		'''
		keyword = raw_input('请输入搜索关键词：'.encode('gbk', 'ignore'))
		encoded_keyword = quote(keyword.decode('gbk').encode('utf8'))
		for page in xrange(1, 70):
			url = 'http://weibo.cn/search/mblog?hideSearchFrame=&keyword=%s&page=%s'%(encoded_keyword, page)
			print "url ", url
			res = session.get(url)
			shortLinks = re.findall(r"<div class=\"c\" id=\"M_(.+?)\">", res.content, re.I)
			print "shortLinks ", shortLinks
			for link in shortLinks:
				turl = 'http://weibo.cn/comment/'+link
				res = session.get(turl)
				#print res.content.encode('gbk', 'ignore')
				if len(re.findall("target weibo does not exist!", res.content, re.I)) == 0:
					user_ids = re.findall(r"uid=([0-9]+)&amp", res.content, re.I)
					if len(user_ids) != 0:
						user_id = user_ids[0]
						print "user_id ", user_id
						with open('mids/mid_%s_%s_jiekuan.txt'%(keyword,self.today), 'a') as f:
							f.write(str(self.tool.url_to_mid(link))+' '+'http://www.weibo.com/u/%s'%(user_id)+'\n')
						f.close()

	def getMidsProcess(self, user, fn2):
		login = Login()
		login.loginWithCookies(user)		
		fn1 = 'mids/mids_%s_'%(user)+self.today+'.txt'
		self.getMids(fn2, fn1)	#fn2:输入uid列表文件，fn1:输出mid列表文件

def test(user, fn):
	crawler = Mid()
	crawler.getMidsProcess(user, fn)

if __name__ == '__main__':
	# read in cookie users
	with open('login_users_2.txt') as f:
		users = f.readlines()
	f.close()
	'''
	# read in uid list filename
	fuid = ''
	while not os.path.exists(fuid):
		fuid = raw_input('请输入uid列表文件路径： '.encode('gbk', 'ignore'))
	with open(fuid) as f:
		lines = f.readlines()
	f.close()
	num_users = len(users)
	#uids = []
	for i in xrange(len(lines)):
		out_name = fuid.split('.')[0]+'_'+str(i%num_users)+'.txt'
		print out_name
		if out_name not in uids:
			uids.append(out_name)
		with open(out_name, 'a') as fout:
			fout.write(lines[i])
		fout.close()
	'''
	uids = ['commenters/commenters_jiekuan_20160722_nodup_0.txt\n','commenters/commenters_jiekuan_20160722_nodup_1.txt\n','commenters/commenters_jiekuan_20160722_nodup_2.txt\n',
	'commenters/commenters_jiekuan_20160722_nodup_3.txt\n','commenters/commenters_jiekuan_20160722_nodup_4.txt\n','commenters/commenters_jiekuan_20160722_nodup_5.txt\n','commenters/commenters_jiekuan_20160722_nodup_6.txt\n',
	'commenters/commenters_jiekuan_20160722_nodup_7.txt\n']
	# multiprocessing
	count = 0
	plist = []
	num_users = len(users)
	for i in xrange(num_users):
		count += 1
		p = Process(target = test, args = (users[i].strip('\n'), uids[i].strip('\n'),))
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
			fn1 = 'mids/mids_'+self.today+'.txt'
			mid = Mid()
			#fn2 = raw_input('请输入uid列表文件路径： '.encode('gbk', 'ignore'))	#uid列表
			#while os.path.exists(fn2) == False:
			#	fn2 = raw_input('请输入uid列表文件路径： '.encode('gbk', 'ignore'))
			#mid.getMids(fn2, fn1)
			mid.getMidByKeyword()
			#if flag=='editfailure':
			#	print "该账号发送评论过于频繁，已被禁！转到下一账号".encode('gbk', 'ignore')
			#	continue
			#else:
			break
	f.close()
	#mid.removeDuplicates(fn1)
	'''

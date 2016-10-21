#-*-coding:utf8-*-

from login import *

class Follower():
	def __init__(self):
		pass

	def traverSet(self,S, uid, filename):
		with open(filename,'a') as f:
			for k in S:
				fan_uid = re.findall(r"http://weibo.cn/u/([0-9]+)", k, re.I)[0]
				f.write('http://www.weibo.com/u/'+fan_uid+' '+uid+'\n')
		f.close()

	def getUrlContent(self,url, uid, filename):
		re_Userinfo = re.compile(r'valign="top"><a href="(http://weibo.cn\/u\/\d+)')
		req = session.get(url)
		S = set(re_Userinfo.findall(str(req.text)))		# S starts with weibo.cn/?
		self.traverSet(S, uid, filename)

	def getFansUrl(self,uid, filename):
		'''
		获得uid的粉丝列表
		'''
		url = "http://weibo.cn/%s/fans"%uid
		req = session.get(url)
		req = BeautifulSoup(req.text,"html.parser")
		re_PageNum = re.compile(r'\/(\d+)页')
		pageList = re_PageNum.findall(str(req))
		if len(pageList) != 0:
			page_num = pageList[0]
			print 'page_num:',page_num
			for pnum in range(1,int(page_num)+1):
				furl = "%s?page=%s"%(url,str(pnum))
				self.getUrlContent(furl, uid, filename)

	def traverseBigV(self, filename1, filename2):
		uidList = [line.strip('\n') for line in open(filename1)]
		for k in xrange(len(uidList)):
			uid = uidList[k]
			self.getFansUrl(uid, filename2)
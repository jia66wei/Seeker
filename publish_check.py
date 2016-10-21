#-*-coding:utf8-*-
#@author by tingting
#

from login import *

class Check():

	def check(self, uids, mid):

		url = 'http://weibo.cn/comment/'+ mid
		res = session.get(url)
		print "url: ", url

		cnt = 0
		while len(res.content) == 0 and cnt < 5:
			time.sleep(1)
			res = session.get(url)
			cnt += 1

		fout = 'Comment/Comment_log.txt'

		if len(res.content) == 0:
			print "~~~~~~~~~~~~~~~~~~~~~~~null~~~~~~~~~~~~~~~~~~~~~~~"
			return
		else:
			text = re.sub(' ', '', res.content)
			contents = re.findall(r"\"评论并转发\"name=\"rt\"/></div>(.*?)</span></div><div", text, re.I)
			content = re.findall(r"class=\"s\"></div>(.*?)</span></div><div", text, re.I)
			for i in range(1, len(content)):
				contents.append(content[i])
	
		cdict = {}
		flag = 0
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
			if uid[0] in uids:
				flag = uid[0]

		if flag != 0:
			print '推送成功！'
			with open(fout, 'a') as f:
				f.write(cdict[flag])
		else:
			print '推送失败~~~~~~~~~~~~~~！'

if __name__ == '__main__':

	with open('haha.txt') as f:
		mids = [l.strip() for l in f]
	print mids

	uids = ['1691024037', '024037','1714118467']


	login = Login()
	login.loginWithCookies('1810001095')
	n2i = Nickname2ID()
	for x in xrange(0, len(mids)):
		n2i.check(uids, mids[x])

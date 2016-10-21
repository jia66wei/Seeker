#!/bin/sh

uid=('user/uid_publishMblog.txt' 'user/jiawei.txt' 'user/uid_joke.txt' 'user/uid_hot.txt' 'user/uid_fanyi.txt' 'user/uid_ice.txt')
ad=('data/20161010/p2pCN.txt' 'ad/ad_joke.txt' 'ad/ad_hot.txt' 'ad/ad_wb.txt' 'ad/ad_content.txt')

python autoPublish.py ${uid[0]}  ${ad[0]} 

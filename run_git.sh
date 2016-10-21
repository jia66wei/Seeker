#!/bin/sh
#@author:jiawei
#@use:update git info

function git_fun()
{
	date=`date`
	echo '############getting git status...###########'
	git status
	echo '############adding modified file...###########'
	sleep 2
	git add .
	echo '############getting new git status...###########'
	sleep 2
	git status
	echo '############commit git...###########'
	sleep 2
	git commit -m "updata at $date "
	echo '############push git...###########'
	sleep 2
	git push origin master
}

#调用git函数
git_fun

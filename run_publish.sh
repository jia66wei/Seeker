#!/bin/sh

#uid=('user/uid_joke.txt' 'user/uid_hot.txt' 'user/uid_fanyi.txt' 'user/uid_ice.txt' 'user/uid_hot_tweet.txt' 'user/uid_commenter_tweet.txt' 'user/uid_content.txt')

uid=('user/20161010/uid_active.txt-a' 'user/20161010/uid_active.txt-b' 'user/20161010/uid_comment_car.txt' 'user/20161010/uid_comment_car_mblog.txt' 'user/20161010/uid_comment_fangchan.txt' 'user/20161010/uid_comment_fangchan_mblog.txt' 'user/20161010/uid_keyword_car.txt' 'user/20161010/uid_keyword_fangchan.txt')
ad=('ad/ad_fangchan_1020.txt' 'ad/ad_car_1020.txt' 'ad/ad_joke.txt' 'ad/ad_hot.txt' 'ad/ad_wb.txt' 'ad/ad_content.txt')

dir='data/20161010'
mids=('active_user.txt-aa' 'active_user.txt-ab' 'hot_comment_car.txt' 'hot_comment_car_mblog.txt' 'hot_comment_fangchan.txt' 'hot_comment_fangchan_mblog.txt' 'keyword_v_car.txt' 'keyword_v_fangchan.txt')

#test
#python autoComment.py ${uid[0]}  $dir/${mids[3]} ${ad[1]} 
##python autoComment.py ${uid[1]}  $dir/${mids[1]} ${ad[1]} &

##python autoComment.py ${uid[2]}  $dir/${mids[2]} ${ad[1]} &
#python autoComment.py ${uid[3]}  $dir/${mids[3]} ${ad[1]} &

##python autoComment.py ${uid[4]}  $dir/${mids[4]} ${ad[0]} &
#python autoComment.py ${uid[1]}  $dir/${mids[5]} ${ad[0]} 

#python autoComment.py ${uid[6]}  $dir/${mids[6]} ${ad[1]} &
#python autoComment.py ${uid[7]}  $dir/${mids[7]} ${ad[0]} 
#hot tweet
#python autoComment.py ${uid[4]}  ${mids[5]} ${ad[2]} 

#comment tweet
python autoComment.py ${uid[5]}  ${mids[5]} ${ad[0]} 

#content
#python autoComment.py ${uid[6]}  ${mids[7]} ${ad[3]} 

#joke
#python autoComment.py ${uid[0]}  ${mids[1]} ${ad[0]} 

#hot
#python autoComment.py ${uid[1]}  ${mids[2]} ${ad[1]} 

#fani
#python autoComment.py ${uid[2]}  ${mids[3]} 'no_file_fanyi'

#ice
#python autoComment.py ${uid[3]}  ${mids[4]} 'no_file_ice'



#!/usr/bin/env python
#coding:utf-8

# 用作linux环境下的bilibili弹幕姬
# read the danmaku to the file and display with Tkinter

import os
import json
import time
import requests
import sys
import Tkinter
import thread

reload(sys) 
sys.setdefaultencoding('utf-8') 

root = Tkinter.Tk()
root.title("Bilibili Danmaku")
root.attributes("-topmost", 1)

def applyBilibiliDanmu():
    f = requests.post("http://live.bilibili.com/ajax/msg", data=form)
    danmu_json = json.loads(f.text, encoding="utf-8")
    danmu_list = danmu_json["data"]["room"]
    return danmu_list

def compare_time(l_time,start_t,end_t):

    s_time = time.mktime(time.strptime(start_t,'%Y-%m-%d %H:%M:%S')) # get the seconds for specify date

    e_time = time.mktime(time.strptime(end_t,'%Y-%m-%d %H:%M:%S'))

    log_time = time.mktime(time.strptime(l_time,'%Y-%m-%d %H:%M:%S'))

   

    if (float(log_time) >= float(s_time)) and (float(log_time) <= float(e_time)):

        return True

    return False

class danMu():
    def __init__(self, text, uid, nickname, isadmin, medal, timeline):
        # text 弹幕
        # isadmin 是否是当前监听的直播间的管理员或主播
        # medal 当前所佩戴勋章
        # timeline 发弹幕的日期时间
        self.text = text
        self.uid = uid
        self.nickname = nickname
        self.isadmin = isadmin
        self.medal = medal
        self.timeline = timeline

    def getMedal(self):
        return self.medal

    def getText(self):
        return self.text

    def getTimeline(self):
        return self.timeline

    def getNickname(self):
        return self.nickname

    def getUid(self):
        return self.uid
    
    def getIsadmin(self):
        # 管理员和主播为1，其余为0
        return self.isadmin

def readDanmaku():
	while 1:
	    time.sleep(1)
	    f = file("danmu.txt","w")
	    danmu_list = applyBilibiliDanmu()
	    #last_timeline = "2016-1-1 00:00:00"
	    for danmu in danmu_list:
		# 新建一个弹幕实例
		p = danMu(danmu["text"], danmu["uid"], danmu["nickname"],
			  danmu["isadmin"], danmu["medal"], danmu["timeline"])
		medal = p.getMedal()
		result = ''
		if p.getIsadmin() == 1:
			result = "【管理】"
		if len(medal) != 0:
			result = result.encode('utf-8') + "【"+medal[1].encode('utf-8')+"-"+str(medal[0]).encode('utf-8')+"】"
		text = result.encode('utf-8')+p.getNickname().encode('utf-8')+" said: "+p.getText().encode('utf-8')+"\n"
		f.write(text)
	    print "Get Danmaku Refreshed"

	    f.close()

def displayDanmaku():
    while 1:
        time.sleep(3)
	list_danmu.delete(0,Tkinter.END)
	f = file("danmu.txt","r")

	while 1:
		line = f.readline()
		line=line.strip('\n')
		if not line:
		    break
		list_danmu.insert(0,line)

	f.close()
	list_danmu.pack()
	print "Read Danmaku Refreshed"

def getThread():
	thread.start_new_thread(readDanmaku, ())

def readThread():
	thread.start_new_thread(displayDanmaku, ())

def setRoom():
	global form
	roomId =  entry.get()  # 监听直播间号
	#print roomId
	if roomId=="":
		print 'Connect Error! Please Enter Your Room Id!'
	else:
		form = {"roomid": roomId}
		print "Connect to Room "+ roomId + " Success!"

entry = Tkinter.Entry(root, text="0")
entry.pack()

Tkinter.Button(root, text="Connect to the Room", width=50, relief="flat", command=setRoom).pack()

Tkinter.Button(root, text="Start Getting Danmaku", width=50, relief='flat', command=getThread).pack()
Tkinter.Button(root, text="Start Reading Danmaku", width=50, relief='flat', command=readThread).pack()

list_danmu = Tkinter.Listbox(root,height=15,width=50)    

root.mainloop()

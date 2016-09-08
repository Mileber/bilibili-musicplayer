#coding=utf-8
#依赖库
#pip install requests
#pip install pygame
#pip install eyed3
import json
import time
import requests
import pygame
import eyed3

roomId = "1187003"  #修改双引号中对应的roomId
form = {"roomid": roomId}
songFlag = u"python点歌机 "  #修改双引号中对应的点歌标志
songFlageLen = len(songFlag.encode("utf-8"))


class danMu():
    def __init__(self, text, uid, nickname, timeline, isadmin, vip, svip,
                 medal, title, user_level, rnd):
        self.text = text
        self.uid = uid
        self.nickname = nickname
        self.timeline = timeline
        self.isadmin = isadmin
        self.vip = vip
        self.svip = svip
        self.medal = medal
        self.title = title
        self.user_level = user_level
        self.rnd = rnd

    def isSong(self):
        if self.text.find(songFlag) != -1:
            keyword = self.text.encode("utf-8")[self.text.encode("utf-8").find(
                songFlag.encode("utf-8")) + songFlageLen:]
            return keyword
        else:
            return -1


def applyBilibiliDanmu():
    f = requests.post("http://live.bilibili.com/ajax/msg", data=form)
    danmu_json = json.loads(f.text, encoding="utf-8")
    danmulist = danmu_json["data"]["room"]
    return danmulist


def applyQQMusic(keyword):
    url = "http://route.showapi.com/213-1"
    send_data = {
        "showapi_appid": "24166",
        "showapi_sign": "5197f4c5ac6c4df993739392d741d579",
        "keyword": keyword,
        "page": "1"
    }
    g = requests.post(url, data=send_data)
    musicjson = json.loads(g.text, encoding="utf-8")
    musiclist = musicjson["showapi_res_body"]["pagebean"]["contentlist"]
    if len(musiclist) == 0:
        return -1
    else:
        return musiclist


def downloadMusic(downloadLink):
    musicfile = requests.get(downloadLink)
    music = open("temp.mp3", "wb")
    music.write(musicfile.content)
    music.close()


def playMusic(keyword):
    musictime = format(eyed3.load("temp.mp3").info.time_secs)
    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play(loops=0, start=0.0)
    print u"正在播放" + unicode(keyword, "utf-8")
    time.sleep(float(musictime))
    pygame.mixer.music.stop()
    pygame.quit()


while 1:
    #初始化歌曲列表
    songList = []
    #获取直播间弹幕
    danmulist = applyBilibiliDanmu()
    for danmu in danmulist:
        #新建一个弹幕的实例
        p = danMu(danmu["text"], danmu["uid"], danmu["nickname"],
                  danmu["timeline"], danmu["isadmin"], danmu["vip"],
                  danmu["svip"], danmu["medal"], danmu["title"],
                  danmu["user_level"], danmu["rnd"])
        #将弹幕列表中所有的点歌歌曲存放到songList中
        if p.isSong() != -1:
            songList.append(p.isSong())
    #如果songList为空，则没有点歌信息
    if len(songList) == 0:
        print u"当前没有点歌信息，等待点歌"
    else:
        keyword = songList[-1]
        #通过keyword搜索有获得值
        if applyQQMusic(keyword) != -1:
            musicList = applyQQMusic(keyword)
            downloadLink = musicList[0]["downUrl"]
            #下载并播放载歌曲
            downloadMusic(downloadLink)
            playMusic(keyword)
    print u"等待点歌"
    time.sleep(5)

#!/usr/bin/python
#coding:utf-8

import os
import json
import time
import requests
import MySQLdb

roomId = "208588"   # 监听直播间号
form = {"roomid": roomId}
flag = u"MC服务器 "  # 新用户注册，要求发送的弹幕格式
flagChangeQQ = u"换qq "  # 更新qq弹幕格式
flagLen = len(flag.encode("utf-8"))
flagChangeQQLen = len(flagChangeQQ.encode("utf-8"))


def applyBilibiliDanmu():
    f = requests.post("http://live.bilibili.com/ajax/msg", data=form)
    danmu_json = json.loads(f.text, encoding="utf-8")
    # print json.dumps(danmu_json, ensure_ascii=False)
    danmu_list = danmu_json["data"]["room"]
    return danmu_list

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
    
    def getMCServerRegister(self):
        if self.text.find(flag) != -1:
            qqKeyword = self.text.encode("utf-8")[self.text.encode("utf-8").find(
                flag.encode("utf-8")) + flagLen:]
            return qqKeyword
        else:
            return -1
    
    def getQQchanged(self):
        if self.text.find(flagChangeQQ) != -1:
            qqKeyword = self.text.encode("utf-8")[self.text.encode("utf-8").find(
                flagChangeQQ.encode("utf-8")) + flagChangeQQLen:]
            return qqKeyword
        else:
            return -1

    def getMedal(self):
        return self.medal

    def getNickname(self):
        return self.nickname

    def getUid(self):
        return self.uid
    
    def getIsadmin(self):
        # 管理员和主播为1，其余为0
        return self.isadmin

def createDatabase():
    # 如果数据表已经存在使用 execute() 方法删除表。
    cursor.execute("DROP TABLE IF EXISTS FANS")

    # 创建数据表SQL语句
    sql = """CREATE TABLE FANS (
            UID  CHAR(20) NOT NULL PRIMARY KEY,
            NICKNAME  CHAR(50) NOT NULL,
            ISADMIN CHAR(5) NOT NULL,  
            MEDAL CHAR(5) NOT NULL,
            QQ CHAR(20) NOT NULL)"""

    cursor.execute(sql)

def selectFans(uid):
    # SQL 查询语句
    sql = "SELECT * FROM FANS WHERE UID = '%s'" % (uid)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        if len(results) != 0:
            return 1
        else:
            return -1
    except:
        print "Error: unable to fecth data"

def insertFans(uid, nickname, isadmin, medal, qq):
    # SQL 插入语句
    sql = "INSERT INTO FANS(UID, NICKNAME, ISADMIN, MEDAL, QQ) VALUES ('%s', '%s', '%s', '%s', '%s' )" % (uid, nickname.encode("utf-8"), isadmin, medal, qq)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        print sql
        db.rollback()
    
def updateFans(uid, nickname, isadmin, medal):
    # SQL 更新语句
    sql = "UPDATE FANS SET NICKNAME = '%s', ISADMIN = '%s', MEDAL = '%s' WHERE UID = '%s'" % (nickname, isadmin, medal, uid)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()

def updateQQ(uid, qq):
    # SQL 更新语句
    sql = "UPDATE FANS SET QQ = '%s' WHERE UID = '%s'" % (qq, uid)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    
#def deleteFans():

# 打开数据库连接
# 参数：用户名 密码 数据库名
db = MySQLdb.connect("localhost","root","123456","bilibili" ,charset='utf8')

# 使用cursor()方法获取操作游标 
cursor = db.cursor()

# 创建数据库
createDatabase()

while 1:
    danmu_list = applyBilibiliDanmu()
    for danmu in danmu_list:
        # 新建一个弹幕实例
        p = danMu(danmu["text"], danmu["uid"], danmu["nickname"],
                  danmu["isadmin"], danmu["medal"], danmu["timeline"])
        medal = p.getMedal()
        if len(medal) != 0:
            if medal[1] == u"十六" and medal[0] >=7:
                # 用户佩戴十六勋章且勋章等级大于等于7
                if p.getQQchanged() != -1:
                    # 用户发送弹幕包含flagQQChange关键字
                    isExist = selectFans(p.getUid())
                    if isExist == 1:
                        # 如果用户已存在，更新数据
                        updateQQ(p.getUid(), p.getQQchanged())
                        
                elif p.getMCServerRegister() != -1:
                    # 用户发送弹幕包含flag关键字
                    isExist = selectFans(p.getUid())
                    if isExist == 1:
                        # 如果用户已存在，更新数据
                        updateFans(p.getUid(), p.getNickname(), p.getIsadmin(), medal[0])
                        if(selectFans(p.getUid()) == 1):
                            print u"更新用户名，勋章，管理员权限成功"
                        else:
                            print u"更新数据失败"
                    elif isExist == -1:
                        # 用户不存在，创建用户
                        insertFans(p.getUid(), p.getNickname(), p.getIsadmin(), medal[0], p.getMCServerRegister())
                        if(selectFans(p.getUid()) == 1):
                            print u"插入数据成功"
                        else:
                            print u"插入数据失败"
                

# 关闭数据库连接
db.close()           


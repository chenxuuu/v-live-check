#coding:utf-8
import time
import os
import sys
import json
import urllib
import urllib.request
import re
import config

#设置UA，防止屏蔽
opener=urllib.request.build_opener()
opener.addheaders=[('Mozilla/5.0 (Windows NT 10.0; Win64; rv:60.0) Gecko/20100101 Firefox/60.0')]
urllib.request.install_opener(opener)

#检查youtube频道是否开启
def youtube(channel):
    try:
        url = "https://www.youtube.com/channel/"+channel+"/live"
        html = urllib.request.urlopen(url,timeout=5).read().decode('utf-8')
        infore = re.compile(r'ytplayer.config *= *(.+?});',re.DOTALL)
        matchObj = infore.findall(html)
        infoAll = json.loads(matchObj[0])
        info = json.loads(infoAll['args']['player_response'])
        return {
            'live' : info['videoDetails']['isLive'],
            'title' : info['videoDetails']['title'],
            'url' : "https://youtu.be/"+info['videoDetails']['videoId'],
            'image' : info['videoDetails']['thumbnail']['thumbnails'][len(info['videoDetails']['thumbnail']['thumbnails'])-1]['url'],
            'channel' : info['videoDetails']['channelId']
        }
    except Exception as e:
        #print('shit')
        #print(e)
        return {'live' : False}

#检查bilibili直播间是否开启
def bilibili(id):
    try:
        url = "https://api.live.bilibili.com/room/v1/Room/get_info?room_id="+str(id)
        html = urllib.request.urlopen(url,timeout=5).read().decode('utf-8')
        info = json.loads(html)
        return {
            'live' : info['data']['live_status'] == 1,
            'title' : info['data']['title'],
            'image' : info['data']['user_cover'],
            'url' : "https://live.bilibili.com/"+str(id)
        }
    except Exception as e:
        return {'live' : False}

#检查twitcasting直播间是否开启
def twitcasting(channel):
    try:
        url = "https://twitcasting.tv/"+channel
        html = urllib.request.urlopen(url,timeout=5).read().decode('utf-8')
        infore = re.compile(r'TwicasPlayer.start\((.+?})\);',re.DOTALL)
        matchObj = infore.findall(html)
        info = json.loads(matchObj[0])
        return {
            'live' : info['isOnlive'],
            'url' : url,
            'image' : "https:"+info['posterImage']
        }
    except Exception as e:
        return {'live' : False}


def all():
    return
    for channel in config.twitcastingList:
        print("check",config.twitcastingList[channel])
        status = twitcasting(channel)
        print(status['live'])
    for channel in config.bilibiliList:
        print("check",config.bilibiliList[channel])
        status = bilibili(channel)
        print(status['live'])
    #检查youtube
    for channel in config.youtubeList:
        print("check",config.youtubeList[channel])
        status = youtube(channel)
        print(status['live'])
all()


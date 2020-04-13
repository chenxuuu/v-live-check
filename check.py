#coding:utf-8
import time
import os
import sys
import json
import urllib
import urllib.request
import re
import config

#检查youtube频道是否开启
def youtube(channel):
    try:
        url = "https://www.youtube.com/channel/"+channel+"/live"
        html = urllib.request.urlopen(url,timeout=5).read().decode('utf-8')
        infore = re.compile(r'ytplayer.config *= *(.+?});',re.DOTALL)
        matchObj = infore.findall(html)
        if not matchObj:
            return
        infoAll = json.loads(matchObj[0])
        info = json.loads(infoAll['args']['player_response'])
        return {
            'live' : info['videoDetails']['isLive'],
            'title' : info['videoDetails']['title'],
            'url' : "https://youtu.be/"+info['videoDetails']['videoId'],
            'pic' : info['videoDetails']['thumbnail']['thumbnails'][len(info['videoDetails']['thumbnail']['thumbnails'])-1]['url'],
            'channel' : info['videoDetails']['channelId']
        }
    except Exception as e:
        #print('shit')
        #print(e)
        return {'live' : False}

def all():
    #检查youtube
    for channel in config.youtubeList:
        print("check",config.youtubeList[channel])
        status = youtube(channel)
#all()

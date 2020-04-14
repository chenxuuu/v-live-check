#coding:utf-8
import time
import os
import sys
import json
import urllib
import urllib.request
import re
import config
import numpy
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

#设置UA，防止屏蔽
opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; rv:60.0) Gecko/20100101 Firefox/60.0')]
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

#检查fc2直播间是否开启
def fc2(channel):
    try:
        url = "https://live.fc2.com/api/memberApi.php?channel=1&profile=1&user=1&streamid="+str(channel)
        html = urllib.request.urlopen(url,timeout=5).read().decode('utf-8')
        info = json.loads(html)
        return {
            'live' : info['data']['channel_data']['is_publish'] == 1,
            'info' : info['data']['profile_data']['info'],
            'image' : info['data']['profile_data']['image'],
            'title' : info['data']['profile_data']['name'],
            'url' : 'fc2:'+str(channel)
        }
    except Exception as e:
        return {'live' : False}

#获取参数
def get(file):
    if os.path.exists(file):
        return numpy.load(file, allow_pickle=True).item()
    else:
        return {}

#保存参数
def set(file,data):
    numpy.save(file,data)

#推送消息到mqtt
def sendMqtt(data,name):
    client = mqtt.Client()
    try:
        #服务器请自行修改，需要传入参数
        client.connect(sys.argv[1], 1883, 60)
        data['name'] = name
        #topic请根据需要自行修改，需要传入参数
        pub = client.publish("live/"+sys.argv[2],json.dumps(data,ensure_ascii=True))
        pub.wait_for_publish()
        client.disconnect()
        text = data['name']+"\r\n"
        if 'title' in data:
            text = text+data['title']+"\r\n"
        text = text+data['url']
        url = "https://api.telegram.org/"+sys.argv[3]+"/sendPhoto?chat_id="+sys.argv[4]+"&photo="+urllib.parse.quote(data['image'])
        url = url+"&caption="+urllib.parse.quote(text)
        html = urllib.request.urlopen(url,timeout=5).read().decode('utf-8')
    except Exception as e:
        print(e)

#与上次状态对比，如有变化则更新
def refresh(status,data,channel,name):
    if channel in data:
        if not status['live']:
            del data[channel]
            print("channel close",status)
    else:
        if status['live']:
            data[channel] = True
            print("channel open",status)
            #推送消息
            sendMqtt(status,name)


#执行任务
def all():
    #检查twitcasting
    tdata = get('tdata.npy')
    for channel in config.twitcastingList:
        #print("check twitcasting",config.twitcastingList[channel])
        status = twitcasting(channel)
        refresh(status,tdata,channel,config.twitcastingList[channel])
    set('tdata.npy',tdata)
    #检查bilibili
    bdata = get('bdata.npy')
    for channel in config.bilibiliList:
        #print("check bilibili",config.bilibiliList[channel])
        status = bilibili(channel)
        refresh(status,bdata,channel,config.bilibiliList[channel])
    set('bdata.npy',bdata)
    #检查youtube
    ydata = get('ydata.npy')
    for channel in config.youtubeList:
        #print("check youtube",config.youtubeList[channel])
        status = youtube(channel)
        refresh(status,ydata,channel,config.youtubeList[channel])
    set('ydata.npy',ydata)
    #检查fc2
    fdata = get('fdata.npy')
    for channel in config.fc2List:
        #print("check fc2",config.fc2List[channel])
        status = fc2(channel)
        refresh(status,fdata,channel,config.fc2List[channel])
    set('fdata.npy',fdata)
    print('done')
all()


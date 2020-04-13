#coding:utf-8
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json


def send(data):
    client = mqtt.Client()
    client.username_pw_set("admin", "123")
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect("mqtt.papapoi.com", 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()

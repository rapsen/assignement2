import paho.mqtt.subscribe as subscribe
import json
import ASS_2_SQLdb
from ASS_2_robot import time_change

database = ASS_2_SQLdb

def on_message_print(client, userdata, message):
    #print("%s %s" % (message.topic, message.payload))
    jsonDATA = json.loads(message.payload)
    #print(jsonDATA)
    time = jsonDATA["time"]
    st=time_change(time)
    jsonDATA["time"]=st
    database.handle_mess(jsonDATA)

subscribe.callback(on_message_print, "ii22/telemetry/#", hostname="broker.mqttdashboard.com")

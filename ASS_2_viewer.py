from flask import Flask, render_template, request, jsonify
import paho.mqtt.subscribe as subscribe
from flask_mqtt import Mqtt
import sqlite3
import ASS_2_SQLdb
from ASS_2_robot import Robot, time_change
import json

# test git

server = Flask(__name__)
database = ASS_2_SQLdb

# Database
conn = sqlite3.connect('robotDB4.db', check_same_thread=False) # , check_same_thread=False

# MQTT
server.config['MQTT_BROKER_URL'] = 'broker.mqttdashboard.com'
server.config['MQTT_BROKER_PORT'] = 1883
server.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
server.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password
server.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
server.config['MQTT_TLS_ENABLED'] = False  # If your server supports TLS, set it True
topic = 'ii22/telemetry/#' #"ii22/telemetry/#"

mqtt_client = Mqtt(server)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topic) # subscribe topic
   else:
       print('Bad connection. Code:', rc)

#@mqtt_client.on_message()
#def on_message_print(client, userdata, message):
    #print("%s %s" % (message.topic, message.payload))
    #jsonDATA = json.loads(message.payload)
    #print(jsonDATA)
    #time = jsonDATA["time"]
    #st = time_change(time)
    #jsonDATA["time"]=st
    #database.handle_mess(jsonDATA)

#subscribe.callback(on_message_print, "ii22/telemetry/#", hostname="broker.mqttdashboard.com")

#@server.route('/data', methods=['POST'])
#def response():
    #print("Got it")
    #message = request.json
    #print(message)
    #database.handle_mess()
    #return f"Server recieved message {message}"

@server.route("/<robot>", methods=["GET"])
def home(robot) -> str:
    rob_name = Robot(f"{robot}")
    rob = Robot.get_rob_name(rob_name)
    state = Robot.get_rob_state(rob_name)
    lTimeCon = Robot.get_rob_lastTimeCon(rob_name)
    class_state = ""
    if state == "READY-IDLE-STARVED":
        class_state = "idleState"
    elif state == "READY-PROCESSING-EXECUTING":
        class_state = "workingState"
    elif state == "DOWN":
        class_state = "errorState"
    return render_template("web.html", nID=rob ,state=state, class_state=class_state, lstTmCon=lTimeCon)

#@server.route("/order", methods=["POST"])
#def newOrder() -> str:
    #return server.newOrder()

if __name__ == "__main__":
    server.run(debug=True)


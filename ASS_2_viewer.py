from flask import Flask, render_template, request
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
import json

from ASS_2_SQLdb import handle_mess
from ASS_2_robot import Robot, time_change

server = Flask(__name__)
threadStarted = False

@server.route('/thread/start', methods=['GET'])
def startThreads():
    print("Start threads attempt")
    global threadStarted
    if (threadStarted):
        return "Threads have started already"

    else:
        threadStarted=True
        #Mqtt
        x = threading.Thread(target=startSubscription)
        x.start()
        return "Starting threads"

@server.route("/event", methods=['POST'])
def robotMessage() -> str:
    event = request.json
    robID = event["deviceId"]
    event = json.dumps(event)
    publish.single(f"ii22/telemetry/{robID}", event, hostname="broker.mqttdashboard.com")
    return "Hello"

@server.route("select/<robot>", methods=["GET"])
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
    return render_template("web.html",nID=rob ,state=state, class_state=class_state, lstTmCon=lTimeCon)

#Mqtt on message
def on_message(client, userdata, msg):
    print("mqtt.on_message")
    jsonDATA = json.loads(msg.payload)
    #print(jsonDATA)
    time = jsonDATA["time"]
    st = time_change(time)
    jsonDATA["time"] = st
    rec_msg = handle_mess(jsonDATA)

#Mqtt thread
def startSubscription():
    print("Mqtt subscription started....")
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.mqttdashboard.com")
    client.subscribe("ii22/telemetry/#")#subscribe all nodes
    rc = 0
    while rc == 0:
        rc = client.loop()

if __name__ == "__main__":
    server.run()


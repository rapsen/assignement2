from json import loads, dumps
from flask import Flask, render_template, request
from paho.mqtt.client import Client
import paho.mqtt.publish as publish
from threading import Thread

from ASS_2_SQLdb import handle_mess
from ASS_2_robot import Robot, time_change
from ASS_2_robot import Robot
from controller import controller as c
from config import *


app = Flask(__name__)
threadStarted = False


@app.route("/")
def root() -> str:
    return render_template("web.html")


@app.route("/dashboard")
def dashboard() -> str:
    return render_template("dashboard.html")


@app.route("/historic")
def historic() -> str:
    return render_template("historic.html", robots=c.robots)


@app.route("/alarms")
def alarms() -> str:
    return render_template("alarms.html")


@app.route('/thread/start', methods=['GET'])
def startThreads():
    print("Start threads attempt")
    global threadStarted
    if (threadStarted):
        return "Threads have started already"
    else:
        threadStarted = True
        x = Thread(target=startSubscription)
        x.start()
        return "Starting threads"


@app.route("/event", methods=['POST'])
def robotMessage() -> str:
    event = request.json
    robID = event["deviceId"]
    event = dumps(event)
    publish.single(f"ii22/telemetry/{robID}",
                   event, hostname=BROKER_HOSTNAME)
    return "Hello"


@app.route("/select/<robot>", methods=["GET"])
def home(robot) -> str:
    rob_name = Robot(f"{robot}")
    rob = Robot.get_rob_name(rob_name)
    state = Robot.get_rob_state(rob_name)
    lTimeCon = Robot.get_rob_lastTimeCon(rob_name)
    class_state = ""
    if state == STARVED:
        class_state = "idleState"
    elif state == EXECUTING:
        class_state = "workingState"
    elif state == DOWN:
        class_state = "errorState"
    return render_template("web.html", nID=rob, state=state, class_state=class_state, lstTmCon=lTimeCon)


def on_message(client, userdata, msg):
    #print("mqtt.on_message")
    jsonDATA = loads(msg.payload)
    # print(jsonDATA)
    time = jsonDATA["time"]
    st = time_change(time)
    jsonDATA["time"] = st
    rec_msg = handle_mess(jsonDATA)


def startSubscription():
    print("Mqtt subscription started....")
    client = Client()
    client.on_message = on_message
    client.connect("broker.mqttdashboard.com")
    client.subscribe("ii22/telemetry/#")  # subscribe all nodes
    rc = 0
    while rc == 0:
        rc = client.loop()

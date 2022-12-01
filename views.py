import json
from json import loads, dumps
from flask import Flask, render_template, redirect, request
import paho.mqtt.publish as publish
from threading import Thread

from controller import controller as c
from model import model as m
from config import *


app = Flask(__name__)
threadStarted = False


@app.route("/")
def root() -> str:
    return render_template("web.html")


@app.route("/dashboard")
def _dashboard():
    return dashboard(c.id)


@app.route("/dashboard/<robot>")
def dashboard(robot) -> str:
    id, state, lstTmCon, status = c.dashboard(robot)
    return render_template("dashboard.html", id=id, state=state, lstTmCon=lstTmCon, status=status)


@app.route("/historic")
def historic() -> str:
    id, robots = c.historic()
    return render_template("historic.html", id=c.id, robots=m.robots)


@app.route("/alarms")
def alarms() -> str:
    id = c.alarms()
    return render_template("alarms.html", id=id)

@app.route("/update", methods=["POST"])


@app.route('/thread/start', methods=['GET'])
def startThreads():
    print("Start threads attempt")
    global threadStarted
    if (threadStarted):
        return "Threads have started already"
    else:
        threadStarted = True
        x = Thread(target=c.suscribe())
        x.start()
        return "Starting threads"


@app.route("/event", methods=['POST'])
def robotMessage() -> str:
    event = request.json
    robID = event["deviceId"]
    event = dumps(event)
    publish.single(MQTT_TOPIC+f"{robID}",
                   event, hostname=BROKER_HOSTNAME)
    return "Hello"

""" Backend for Web UI"""
@app.route("/api/historic/")
def historicdata():
    # data = {"deviceId": "rob1", "state": "READY", "time": 1669476872}
    inputdata = m.getRobEffBetTime("rob1", 1669476872, 1669812579)
    data = json.dumps(inputdata)
    return data

@app.route("/api/realstate/")
def realtimestate():
    # data = {"deviceId": "rob1", "state": "READY", "time": 1669476872}
    inputdata = m.getlaststate("rob2")
    data = json.dumps(inputdata)
    return data
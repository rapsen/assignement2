import json
from json import loads, dumps
from flask import Flask, render_template, redirect, request
import paho.mqtt.publish as publish
from threading import Thread

from controller import controller as c
from model import model as m
from config import *
from controller import controller, mqtt, socket
from model import model

# Create the flask application
app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = BROKER_HOSTNAME
app.config['MQTT_BROKER_PORT'] = BROKER_PORT
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False


@app.route("/")
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("dashboard.html", **controller.dashboard())


@app.route("/historic", methods=["GET", "POST"])
def historic() -> str:
    return render_template("historic.html", **controller.historic())


@app.route("/alarms", methods=["GET", "POST"])
def alarms() -> str:
    return render_template("alarms.html", **controller.alarms())


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

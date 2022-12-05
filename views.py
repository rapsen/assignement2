import json
from json import loads, dumps
from flask import Flask, render_template, redirect, request
import paho.mqtt.publish as publish
from datetime import datetime

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
@app.route("/dashboard")
@app.route("/dashboard/<string:id>")
def dashboard_(id: str = controller.id):
    return render_template("dashboard.html", **controller.dashboard(id))


@app.route("/historic", methods=["GET", "POST"])
@app.route("/historic/<string:id>", methods=["GET", "POST"])
def historic(id: str = controller.id) -> str:
    return render_template("historic.html", **controller.historic(id))


@app.route("/alarms", methods=["GET", "POST"])
@app.route("/alarms/<string:id>", methods=["GET", "POST"])
def alarms(id: str = controller.id) -> str:
    return render_template("alarms.html", **controller.alarms(id))


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


@app.template_filter()
def timestamp2date(value, format="%d/%m/%y, %H:%M:%S"):
    # Convert to Helsinki timezone
    return datetime.fromtimestamp(value+60*60*2).strftime(format)

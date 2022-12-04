from datetime import datetime, timedelta
from json import loads, dumps

from flask import request
from flask_mqtt import MQTT_LOG_ERR, Mqtt
from flask_socketio import SocketIO

from config import *
from model import model, iso2timestamp
from database import database

# Create the socket
socket = SocketIO()
# Create the mqtt client
mqtt = Mqtt()


@socket.on('ask')
def ask(deviceId):
    socket.emit('update', data=database.SELECT_ROBOT(deviceId).__dict__)


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = loads(message.payload.decode())
    data['SN'] = data.pop("sequenceNumber")  # Change key for sequnceNumber
    controller.on_message(data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    if level == MQTT_LOG_ERR:
        log.error(f"MQTT Error: {buf}")


class Controller():
    def __init__(self) -> None:
        if len(model.robots):
            self.id = model.robots[0]
        else:
            self.id = None
            log.warning("No robots in database")
        self.robot = model.getRobots()

    def on_message(self, data: dict) -> None:
        event = model.on_message(data)
        log.info(f"MQTT {event.__dict__}")
        socket.emit('update', data=event.__dict__)

    def dashboard(self) -> dict:
        if request.method == "POST":
            self.id = request.form['id']

        return database.SELECT_ROBOT(self.id).__dict__ | {"robots": model.robots}

    def historic(self) -> dict:
        percentages, mtbf = {}, None

        if request.method == "POST":
            percentages, mtbf = controller.efficiency(request.form)

        return {"id": self.id, "robots": model.robots, "efficiency": dumps(percentages), "mean": mtbf}

    def alarms(self) -> dict:
        alarms = {}
        if request.method == "POST":
            alarms = model.getAlarms(**request.form)
        return {"id": self.id, "robots": model.robots, "states": ALARM_STATES, "alarms": alarms}

    def efficiency(self, form: dict) -> dict:
        d, mean = [], "No data"

        id, start, end = form.values()
        self.id = id
        start, end = iso2timestamp(start), iso2timestamp(end)
        d, mean = model.getRobEffBetTime(self.id, start, end)
        return d, mean


# Create istance of the controller
controller = Controller()

from json import loads, dumps

from flask import request
from flask_mqtt import MQTT_LOG_ERR, Mqtt
from flask_socketio import SocketIO

from config import *
from model import model, iso2epoch, epoch2iso
from database import database

# Create the socket IO connection
socket = SocketIO()
# Create the mqtt client
mqtt = Mqtt()


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
        self.id = model.robots[0]
        self.__robot = model.getRobots()

    def on_message(self, data: dict) -> None:
        event = model.on_message(data)
        log.info(f"MQTT {event.__dict__}")
        socket.emit('update', data=event.__dict__)

    def dashboard(self, id=None) -> dict:
        if id is not None:
            self.id = id

        robot = database.SELECT_ROBOT(self.id)

        return {"id": self.id, "robot": robot, "robots": model.robots}

    def historic(self, id=None) -> dict:
        result = {}
        if id is not None:
            self.id = id

        return {"id": self.id, "robots": model.robots} | self.efficiency(request.form)

    def alarms(self, id=None) -> dict:
        alarms = {"start": epoch2iso(), "end": epoch2iso()}
        if request.method == "POST":
            alarms = model.getAlarms(**request.form)
        return {"id": self.id, "robots": model.robots, "states": ALARM_STATES} | alarms

    def efficiency(self, form: dict) -> dict:
        d, mtbf = [], "No data"
        start, end = [epoch2iso()]*2
        if request.method == "POST":
            self.id, start, end = form.values()

        d, mtbf = model.getRobEffBetTime(
            self.id, iso2epoch(start), iso2epoch(end))
        return {"percentage": dumps(d), "mtbf": mtbf, "start": start, "end": end}


# Create istance of the controllers
controller = Controller()

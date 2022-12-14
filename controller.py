from json import loads, dumps
from time import sleep
from threading import Thread

from flask import request, Flask
from flask_mqtt import MQTT_LOG_ERR, MQTT_ERR_SUCCESS, Mqtt
from flask_socketio import SocketIO

from config import *
from model import model, iso2epoch, epoch2iso
from database import database

class __Mqtt(Mqtt):
    """ Just adding thread reconection to the original Mqtt client"""
    def __init__(self, app: Flask = None, connect_async: bool = False, mqtt_logging: bool = False) -> None:
        super().__init__(app, connect_async, mqtt_logging)
        self.subscriber = Thread(target=self.subscription)  

    def subscription(self):
        log.info(f"Suscription Thread started")
        while True:
            if MQTT_TOPIC not in list(mqtt.topics):
                mqtt.subscribe(MQTT_TOPIC)
                log.info(f"MQTT Suscribed to {MQTT_TOPIC}")
            # Wait 1 minute
            sleep(60)
                
# Create the socket IO connection
socket = SocketIO()
# Create the mqtt client with thread
mqtt = __Mqtt()


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = loads(message.payload.decode())
    data['SN'] = data.pop("sequenceNumber")  # Change key for sequnceNumber
    controller.on_message(data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    if level == MQTT_LOG_ERR:
        log.error(f"MQTT Error: {buf}")
        
@mqtt.on_disconnect()
def handle_disconnect():
    log.info(f"MQTT Disconnected")
    mqtt.connected = False

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

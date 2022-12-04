from datetime import datetime, timedelta
from json import loads, dumps

from flask_mqtt import MQTT_LOG_ERR, Mqtt
from flask_socketio import SocketIO

from config import *
from model import model, iso2timestamp

# Create the socket
socket = SocketIO()
# Create the mqtt client
mqtt = Mqtt()


@socket.on('ask')
def ask(deviceId):
    robot = model.db.SELECT_ROBOT(deviceId)
    socket.emit('update', data=robot.__dict__)


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = loads(message.payload.decode())
    controller.handle(data)


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

    def on_message(self, client, userdata, msg):
        model.update(loads(msg.payload))

    def handle(self, data: dict) -> None:
        event = model.handle(data)
        log.info(f"MQTT {event.__dict__}")
        socket.emit('update', data=event.__dict__)

    def dashboard(self, deviceId) -> tuple:
        self.id = deviceId
        robot = model.db.SELECT_ROBOT(self.id)
        return robot.__dict__.values()

    def historic(self) -> tuple:
        return self.id, model.robots

    def efficiency(self, form: dict) -> dict:
        id, start, end = form.values()
        self.id = id
        start, end = iso2timestamp(start), iso2timestamp(end)
        return model.getRobEffBetTime(self.id, start, end)

    def alarms(self) -> tuple:
        return self.id

    def notify(self):
        pass


# Create istance of the controller
controller = Controller()

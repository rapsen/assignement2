from datetime import datetime, timedelta
from json import loads

from flask_mqtt import MQTT_LOG_ERR, Mqtt
from flask_socketio import SocketIO

from config import *
from model import model

# Create the socket
socket = SocketIO()
# Create the mqtt client
mqtt = Mqtt()


@socket.on('ask')
def ask(robot):
    data = model.last_event(robot)
    data['time'] = str(datetime.fromtimestamp(
        data['time']) + timedelta(hours=2))
    socket.emit('update', data=data)


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = loads(message.payload.decode())
    controller.handle(data)
    data['time'] = str(datetime.fromisoformat(
        data['time'][:19]) + timedelta(hours=2))
    socket.emit('update', data=data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    if level == MQTT_LOG_ERR:
        print('Error: {}'.format(buf))


class Controller():
    def __init__(self) -> None:
        self.id = list(model.robots.keys())[0]

    def on_message(self, client, userdata, msg):
        model.update(loads(msg.payload))

    def handle(self, data: dict) -> None:
        model.handle(data)

    def dashboard(self, id: str = None) -> tuple:
        self.id = self.id if id is None else id
        last_time = datetime.fromtimestamp(
            model.robots[self.id].time) + timedelta(hours=2)
        state = model.robots[self.id].state
        return self.id, state, last_time, status(state)

    def historic(self) -> tuple:
        return self.id, list(model.robots.values())

    def alarms(self) -> tuple:
        return self.id

    def notify(self):
        pass


def status(state: str) -> str:
    """ Return the status of the robot """
    if state in [EXECUTING, ACTIVE]:
        status = PROCESSING
    elif state in [BLOCKED, STARVED]:
        status = IDLE
    else:
        status = ERROR
    return status


# Create istance of the controller
controller = Controller()

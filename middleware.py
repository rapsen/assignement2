from flask import Flask, request
import paho.mqtt.publish as publish
import json
import xmltodict

server = Flask(__name__)
SN_counter = {}

"""For subscription"""
# r = post(f'http://192.168.6.2/rest/events/rob1/notifs',
# json={"destUrl": f"http://127.0.0.1:5000/Status_Changed"})

def seq_counter(robId):
    if robId not in SN_counter:
        SN_counter.update({f'{robId}': 0})
    SN_counter[f'{robId}'] += 1
    return SN_counter[f'{robId}']

class Robot:
    def __init__(self, data: dict):
        self.deviceId = data['@deviceId']
        self.state = data['@currentState']
        self.time = data['@dateTime']
        self.event = {}

    def RobotId(self):
        return self.deviceId

    def conToJson(self, count):
        self.event.update({'deviceId': self.deviceId})
        self.event.update({'state': self.state})
        self.event.update({'time': self.time})
        self.event.update({'SN': count})
        jsonev = json.dumps(self.event)
        return jsonev

@server.route("/event", methods=['GET', 'POST'])
def parse_xml() -> str:
    content_dict = xmltodict.parse(request.data)
    mess = content_dict['Envelope']['Message']['IPC2541:EquipmentInitializationComplete']
    ROB = Robot(mess)
    count = seq_counter(ROB.deviceId)
    jsonmess = Robot.conToJson(ROB, count)
    publish.single(f"ii22/robots/{Robot.RobotId(ROB)}", jsonmess, hostname="broker.mqttdashboard.com")

    return f"Sent message {jsonmess}"

if __name__ == "__main__":
    server.run()
from paho.mqtt.client import Client
from json import loads
from model import model as m
from datetime import datetime
from config import *

class Controller():
    def __init__(self) -> None:
        self.id = list(m.robots.keys())[0]
        self.client = Client()

        
    def on_message(self, client, userdata, msg):
        m.update(loads(msg.payload))
        
    def handle_mess(payload):
        print(f"Got message {payload}")
        robotID = payload["deviceId"]
        state = payload["state"]
        time = payload["time"]
        sequenceNr = int(payload["sequenceNumber"])
        insert_robot(robotID, state, time, sequenceNr)
        return payload


    def suscribe(self):
        print("Mqtt subscription started....")
        self.client.on_message = self.on_message
        self.client.connect(BROKER_HOSTNAME)
        self.client.subscribe(MQTT_TOPIC+"#")  # subscribe all nodes
        rc = 0
        while rc == 0:
            rc = self.client.loop()
    
             
    def dashboard(self, id:str) -> tuple:
        self.id = id
        last_time = datetime.fromtimestamp(m.robots[id].time)
        state = m.robots[id].state
        
        match state:
            case "OFF" | "DOWN":
                status = "error"
            case "SETUP" | "READY-IDLE-STARVED" | "READY-IDLE-BLOCKED":
                status = "idle"
            case "READY-PROCESSING-EXECUTING" | "READY-PROCESSING-ACTIVE":
                status ="active"
        
        return self.id, state, last_time, status
    
    def historic(self) -> tuple:
        return self.id, list(m.robots.values())
        
    def alarms(self) -> tuple:
        return self.id
    
    def notify(self):   
        pass
    
        
# Create istance of the controller
controller = Controller()

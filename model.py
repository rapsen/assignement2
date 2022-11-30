import sqlite3
from datetime import datetime
from time import mktime
from config import *


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Event():
    def __init__(self, data: dict):
        self.id = None
        self.deviceId = data['deviceId']
        self.state = data['state']
        self.time = int(data['time'])
        self.sequenceNumber = int(data['sequenceNumber'])

    def __repr__(self) -> str:
        return f"Event: id={self.id} deviceId={self.deviceId} state={self.state} time={self.time} sequenceNumber={self.sequenceNumber}"


class Robot:
    def __init__(self, event: Event):
        self.id = event.deviceId
        self.state = event.state
        self.time = event.time

    def __repr__(self) -> str:
        return f"Robot: id={self.id} state={self.state} time={self.time}"


class Database():
    """ Class to handle database """

    def __init__(self):
        self.database = DATABASE
        self.table = "Event"
        self.request = ""
        self.c = None

        self.connect()

        self.create()

    def connect(self):
        self.connexion = sqlite3.connect(
            self.database, check_same_thread=False)
        self.connexion.row_factory = dict_factory
        self.c = self.connexion.cursor()

    def create(self):
        """ Create the database if it does not exist """

        self.c.execute("""CREATE TABLE IF NOT EXISTS Event (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            deviceId text, 
                            state text, 
                            time text, 
                            sequenceNumber integer
                            );""")

    def execute(self) -> list:
        self.c.execute(self.request)

        return self.c.fetchall()

    def __SELECT(self, element="*", condition=True) -> list:
        """ Private method to request element according to the condition """

        self.request = f"SELECT {element} FROM {self.table} WHERE {condition}"
        # print(self.request)

        return self.execute()

    def __INSERT(self, deviceId, state, sequenceNumber, time):
        """ Private method to insert element """

        self.request = f"INSERT INTO {self.table} (deviceId, state, sequenceNumber, time) \
                         VALUES ('{deviceId}', '{state}', {sequenceNumber}, {time})"
        #print(self.request)

        self.execute()
        
        self.connexion.commit()


    def getAllEvents(self) -> list[Event]:
        return [Event(d) for d in self.__SELECT()]

    def getAllEventByState(self, state: str) -> list[Event]:
        return [Event(d) for d in self.__SELECT(condition=f"state == '{state}'")]

    def getAllEventByRobot(self, deviceId: str) -> list[Event]:
        return [Event(d) for d in self.__SELECT(condition=f"deviceId == '{deviceId}'")]

    def getAllEventByTime(self, start: int, end: int) -> list[Event]:
        return [Event(d) for d in self.__SELECT(condition=f"time BETWEEN {start} AND {end}")]

    def getEventById(self, id: int) -> Event:
        return Event(self.__SELECT(condition=f"id == {id}")[0])

    def getAllDeviceId(self) -> list:
        return self.__SELECT(element="DISTINCT deviceId")

    def getLastEventByRobot(self, deviceId: str) -> Event:
        return self.getAllEventByRobot(deviceId)[-1]
    
    def addEvent(self, event:Event):
        return self.__INSERT(event.deviceId, event.state, event.sequenceNumber, event.time)


class Model():
    def __init__(self):
        # Create the instance of the database
        self.db = Database()
        self.robots = self.getRobots()

    def getRobots(self) -> dict:
        robots = {}

        for deviceId in self.db.getAllDeviceId():
            Id = deviceId['deviceId']
            lastEvent = self.db.getLastEventByRobot(Id)
            robots[Id] = Robot(lastEvent)
        
        return robots

    def addEvent(self, event:Event):
        print("New event in db: ", event)
        self.db.addEvent(event)

    def update(self, data: dict):
        data['time'] = convert(data['time'])
        self.addEvent(Event(dict(data)))
        
def convert(time: str) -> int:
    return int(mktime(datetime.strptime(time[0:26], "%Y-%m-%dT%H:%M:%S.%f").timetuple()))

# Create istance of the model
model = Model()

# Test get methods

# print(model.getAllEvents())
# print(model.getAllEventByState(DOWN))
# print(model.getAllEventByRobot("rob1"))
# print(model.getAllEventByTime(1669476872, 1669477333))
# print(model.getEventById(3))
# print(model.getAllDeviceId())
# print(model.getLastEventByRobot("rob2"))

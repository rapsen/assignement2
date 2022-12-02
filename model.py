from sqlite3 import connect
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
        self.time = data['time']
        self.sequenceNumber = int(data['sequenceNumber'])

        self.convert()

    def __repr__(self) -> str:
        return f"Event: id={self.id} deviceId={self.deviceId} state={self.state} time={self.time} sequenceNumber={self.sequenceNumber}"

    def convert(self):
        if type(self.time) is str:
            self.time = int(mktime(datetime.strptime(
                self.time[0:26], "%Y-%m-%dT%H:%M:%S.%f").timetuple()))


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

        self.connexion = connect(
            self.database, check_same_thread=False)
        self.connexion.row_factory = dict_factory
        self.c = self.connexion.cursor()

    def execute(self) -> list:
        self.c.execute(self.request)

        return self.c.fetchall()

    def __SELECT(self, table=EVENT, element="*", condition=True) -> list:
        """ Private method to request element according to the condition """

        self.request = f"SELECT {element} FROM {table} WHERE {condition}"
        # print(self.request)

        return self.execute()

    def __INSERT(self, table, deviceId, state, sequenceNumber, time):
        """ Private method to insert element """

        self.request = f"INSERT INTO {table} (deviceId, state, sequenceNumber, time) \
                         VALUES ('{deviceId}', '{state}', {sequenceNumber}, {time})"
        # print(self.request)

        self.execute()

        self.connexion.commit()

    def getAllEvents(self) -> Event:
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

    def getLastStateByRobot(self, deviceId: str):
        return self.__SELECT(element="deviceId, state, time", condition=f"deviceId = '{deviceId}' ORDER BY time DESC;")

    def addEvent(self, event: Event):
        return self.__INSERT(EVENT, event.deviceId, event.state, event.sequenceNumber, event.time)

    def getRobEventBetweenTime(self, deviceId: str, start: int, end: int):
        return self.__SELECT(element="deviceId, state, time", condition=f"deviceId = '{deviceId}' and time between '{start}' and '{end}' ORDER BY time ASC;")


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

    def addEvent(self, event: Event):
        print("New event in db: ", event)
        self.db.addEvent(event)

    def last_event(self, id: str) -> Event:
        a = self.db.getLastEventByRobot(id).__dict__
        print(a)
        return a

    def handle(self, data: dict) -> None:
        event = Event(data)
        model.db.addEvent(event)

    def getRobEffBetTime(self, deviceId: str, start, end):
        # sqlSt = f"SELECT state, time FROM robot WHERE deviceId = '{robotID}' and time between " \
        #         f"'{start}' and '{end}' ORDER BY time ASC;"
        # c.execute(sqlSt)
        # list = c.fetchall()
        pass

    def update(self, data: dict):
        # Update database
        data['time'] = convert(data['time'])
        self.addEvent(Event(dict(data)))

    def getlaststate(self, deviceId: str):
        data = self.db.getLastStateByRobot(deviceId)[0]
        return data

    def getRobEffBetTime(self, deviceId: str, start, end):
        """ This function calculates KPIs and Mean Time -> returns dict"""
        list = self.db.getRobEventBetweenTime(deviceId, start, end)
        stateDict = {}
        efficiency = {}
        up_time = 0
        down_time = 0
        infailure_times = []
        for rep in range(len(list) - 1):
            start_dict = list[rep]
            end_dict = list[rep + 1]
            start_time = start_dict["time"]
            end_time = end_dict["time"]
            robot_state = start_dict["state"]

            # When failure is repaired
            if start_dict["state"] == "DOWN" and end_dict["state"] != "DOWN":
                up_time = end_time
            # When failure appear
            elif start_dict["state"] != "DOWN" and end_dict["state"] == "DOWN" and up_time != 0:
                down_time = end_time

            if up_time != 0 and down_time != 0:
                infailure_time = round(down_time - up_time, 1)
                infailure_times.append(infailure_time)
                up_time = 0
                down_time = 0

            if robot_state not in stateDict:
                stateDict.update({robot_state: 0})

            total_time = round(end_time - start_time, 1)

            initialvalue = stateDict[robot_state]
            initialvalue += total_time
            stateDict.update({robot_state: initialvalue})

        total_gathered_time = round(sum(stateDict.values()), 1)

        for rep in stateDict:
            time_state = stateDict[rep]
            perc = round((time_state * 100) / total_gathered_time, 1)
            efficiency.update({rep: perc})

        total_fail_time = sum(infailure_times)
        mean_time = total_fail_time / len(infailure_times)
        efficiency.update({"MEAN": mean_time})
        #print("States:", efficiency)
        return efficiency

    def getRobAlarms(self, deviceId: str, start: int, end: int):
        list = self.db.getRobEventBetweenTime(deviceId, start, end)
        idle_alarm = 60     # alarm time for IDLE state in seconds
        down_alarm = 180    # alarm time for DOWN state in seconds
        alarms = []         # list of alarms
        alarm_id = 0
        for rep in range(len(list) - 1):
            start_dict = list[rep]
            end_dict = list[rep + 1]
            start_time = start_dict["time"]
            end_time = end_dict["time"]

            # Alarms for states IDLE and DOWN
            time_exceed_idle = start_time + idle_alarm
            time_exceed_down = start_time + down_alarm
            if time_exceed_idle < end_time and start_dict["state"] == "READY-IDLE-STARVED":
                mess = f"CAUTION: {deviceId} in {start_dict['state']} state more than {idle_alarm} s"
                alarm_id += 1
                # list of information
                report = alarm_id, mess, start_time
                alarms.append(report)

            if time_exceed_down < end_time and start_dict["state"] == "DOWN":
                mess = f"CAUTION: {deviceId} in {start_dict['state']} state more than {down_alarm} s"
                alarm_id += 1
                # list of information
                report = alarm_id, mess, start_time
                alarms.append(report)

        # print(len(alarms))
        return alarms



def convert(time: str) -> int:
    return int(mktime(datetime.strptime(time[0:26], "%Y-%m-%dT%H:%M:%S.%f").timetuple()))


# Create instance of the model
model = Model()

# Test get methods
# print(model.db.getAllEvents())
# print(model.getAllEventByState(DOWN))
# print(model.getAllEventByRobot("rob1"))
# print(model.getAllEventByTime(1669476872, 1669477333))
# print(model.getEventById(3))
# print(model.getAllDeviceId())
# print(model.getLastEventByRobot("rob2"))
# print(model.getRobEffBetTime("rob2", 1669476872, 1669977340))
# print(model.getlaststate("rob1"))
# print(model.getRobAlarms("rob2", 1669476872, 1669977340))
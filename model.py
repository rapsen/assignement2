from sqlite3 import connect
from datetime import datetime, timedelta
from time import mktime

from config import *


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Robot:
    def __init__(self, data: dict):
        self.deviceId = data['deviceId']
        self.state = data['state']
        self.time = data['time']
        self.convert()

    def __repr__(self) -> str:
        return f"Robot: deviceId={self.deviceId} state={self.state} time={self.time}"

    def convert(self):
        """ Convert the time:
                * to an integer timestamp if time is a string
                * to to an ISO string if time is an integer
        """
        if type(self.time) == str:
            self.time = int(mktime(datetime.strptime(
                self.time.replace(" ", "T")[0:19], ISO_TIME).timetuple()))
        # elif type(self.time) == int:
        #     self.time = str(datetime.fromtimestamp(
        #         self.time) + timedelta(hours=2))


class Event(Robot):
    def __init__(self, data: dict):
        super().__init__(data)
        self.sequenceNumber = int(data['sequenceNumber'])

    def __repr__(self) -> str:
        return f"Event: deviceId={self.deviceId} state={self.state} time={self.time} sequenceNumber={self.sequenceNumber}"

    def robot(self) -> Robot:
        """ Return an Robot instance with event parameter"""
        return Robot(self.__dict__)


class Database():
    """ Class to handle database """

    def __init__(self):
        self.table = "Event"
        self.c = None

        self.connexion = connect(DATABASE, check_same_thread=False)
        self.connexion.row_factory = dict_factory
        self.c = self.connexion.cursor()

        self.create()

    def create(self):
        with open(DATABASE_SCRIPT, 'r') as db:
            script = db.read()

        self.c.executescript(script)
        self.connexion.commit()

    def execute(self, request: str, commit: bool = False) -> list:
        self.c.execute(request)

        if commit:
            self.connexion.commit()

        return self.c.fetchall()

    def __SELECT(self, table: str = EVENT, element: tuple = ('*'), condition: str = True) -> list:
        """ Private method to select element of the table with given condition """

        request = f"SELECT {element} FROM {table} WHERE {condition}"

        return self.execute(request)

    def __INSERT(self, table: str, values: tuple) -> list:
        """ Private method to insert in the table the values """

        request = f"INSERT INTO {table} {TABLES[table]} VALUES {values}"

        self.execute(request, commit=True)

    def __UPDATE(self, table: str, values: list, condition: str = str(True)) -> list[dict]:
        """ Private method to update ALL element of the table with the new values """

        update = ""

        for k, v in values.items():
            update += f"{k}='{v}', " if type(v) is str else f"{k}={v}, "

        request = f"UPDATE {table} SET {update[:-2]} WHERE {condition}"

        self.execute(request, commit=True)

    def getAllRobots(self) -> list[Robot]:
        return [Robot(r) for r in self.__SELECT(table=ROBOT)]

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
        return [d["deviceId"] for d in self.__SELECT(element="DISTINCT deviceId")]

    def getLastEventByRobot(self, deviceId: str) -> Event:
        return self.getAllEventByRobot(deviceId)[-1]

    def getLastStateByRobot(self, deviceId: str):
        return self.__SELECT(element="deviceId, state, time", condition=f"deviceId = '{deviceId}' ORDER BY time DESC;")

    def addEvent(self, event: Event):
        return self.__INSERT(EVENT, (event.deviceId, event.state, event.sequenceNumber, event.time))

    def getRobEventBetweenTime(self, deviceId: str, start: int, end: int):
        return self.__SELECT(element="deviceId, state, time", condition=f"deviceId = '{deviceId}' and time between '{start}' and '{end}' ORDER BY time ASC;")

    def getStateById(self, deviceId: str, state: str) -> list:
        return self.__SELECT(element=f"id,time", condition=f"deviceId='{deviceId}' AND state='{state}'")

    def SELECT_ALL_ROBOT(self):
        return [Robot(d) for d in self.__SELECT(ROBOT)]

    def SELECT_ROBOT(self, deviceId: int):
        return Robot(self.__SELECT(ROBOT, condition=f"{deviceId=}")[0])

    def addRobot(self, robot: Robot):
        return self.__INSERT(ROBOT, (robot.deviceId, robot.state, robot.time))

    def updateRobot(self, robot: Robot):
        deviceId = robot.deviceId
        return self.__UPDATE(ROBOT, robot.__dict__, condition=f"{deviceId=}")


class Model():
    def __init__(self):
        # Create the instance of the database
        self.db = Database()
        self.robots = [r.deviceId for r in self.getRobots()]

    def getRobots(self) -> list:
        return self.db.SELECT_ALL_ROBOT()

    def addEvent(self, event: Event):
        print("New event in db: ", event)
        self.db.addEvent(event)

    def last_event(self, id: str) -> Event:
        a = self.db.getLastEventByRobot(id).__dict__
        print(a)
        return a

    def handle(self, data: dict) -> Event:
        event = Event(data)
        model.db.addEvent(event)
        if event.deviceId in self.robots:
            model.db.updateRobot(event.robot())
        else:
            model.db.addRobot(event.robot())
        return event

    def update(self, data: dict):
        # Update database
        data['time'] = iso2timestamp(data['time'])
        self.addEvent(Event(dict(data)))

    def getlaststate(self, deviceId: str):
        data = self.db.getLastStateByRobot(deviceId)[0]
        return data

    def getRobEffBetTime(self, deviceId: str, start: int, end: int):
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
            if start_dict["state"] == DOWN and end_dict["state"] != DOWN:
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
        mean_time = total_fail_time / \
            len(infailure_times) if len(infailure_times) != 0 else 0
        #efficiency.update({"MEAN": mean_time})
        #print("States:", efficiency)
        return efficiency, mean_time

    def getAlarmForState(self, deviceId: str, timeAlarm: int, state: str):
        robot = self.db.getAllEventByRobot(deviceId)
        EventsInAlarm = []

        for robotState in self.db.getStateById(deviceId, state):
            for i in range(0, len(robot) - 1):

                if (robot[i].id == robotState['id']):

                    #print("time state start ",robot[i-1].time," ",robot[i].time)
                    timesStartState = int(robot[i - 1].time)

                    timeEndState = int(robot[i + 1].time)
                    #print("time state end   ",robot[i+1].time," ",robot[i].time)
                    timeEvent = timeEndState - timesStartState
                    if (timeEvent > timeAlarm):
                        EventsInAlarm.append(robot[i])
                        print(
                            f"/!\ Warning:in event {robot[i].id} device {deviceId} is {timeEvent} seconds in {state} state")

        return EventsInAlarm


def iso2timestamp(time: str) -> int:
    if len(time) < 26:
        time = time + ":00.0"  # Add padings for the seconds
    return int(mktime(datetime.strptime(time[0:26], "%Y-%m-%dT%H:%M:%S.%f").timetuple()))


# Create instance of the model
model = Model()

# Test get methods
# print(model.getAlarmForState('rob1',600,'DOWN'))

# print(model.db.getAllEvents())
# print(model.db.getAllEventByState(DOWN))
# print(model.db.getAllEventByRobot("rob1"))
# print(model.db.getAllEventByTime(1669476872, 1669477333))
# print(model.db.getEventById(3))
# print(model.db.getAllDeviceId())
# print(model.db.getLastEventByRobot("rob2"))
# print(model.getRobEffBetTime("rob2", 1669476872, 1669811095))
# print(model.getlaststate("rob1"))

e = Event({'id': 4190, 'deviceId': 'rob2', 'state': 'READY-PROCESSING-EXECUTING',
          'sequenceNumber': 17730, 'time': int(datetime.now().timestamp())})

# model.addEvent(e)

r = {'deviceId': 'rob2', 'state': 'READY-PROCESSING-EXECUTING',
     'time': int(datetime.now().timestamp())}

# model.db.addRobot(Robot(r))
# model.db.updateRobot(Robot(r))

# print(model.db.SELECT_ROBOT("rob1"))

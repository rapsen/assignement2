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


# Create instance of the database
database = Database()


def test():
    """ Test database operation """

    db = Database()

    r = {'deviceId': 'rob2', 'state': 'READY-PROCESSING-EXECUTING',
         'time': int(datetime.now().timestamp())}

    e = Event({'id': 4190, 'deviceId': 'rob2', 'state': 'READY-PROCESSING-EXECUTING',
               'sequenceNumber': 17730, 'time': int(datetime.now().timestamp())})

    print("#####################  ROBOT  #########################")
    total_robot = db.SELECT_ALL_ROBOT()
    print(total_robot)
    print(f"Total Robot: {len(total_robot)}")
    for robot in total_robot:
        print(f"    {db.SELECT_ROBOT(robot.deviceId)}")

    print("#####################  EVENT  #########################")
    print(f"Total Event: {len(db.getAllEvents())}")
    print("     State:")
    for state in STATES:
        print(f"        {state}: {len(db.getAllEventByState(state))}")
    print("     Robot:")
    for robot in total_robot:
        print(
            f"        {robot.deviceId}: {len(db.getAllEventByRobot(robot.deviceId))}")

    start, end = 1669476872, 1669477333

    print(f"     Between {datetime.fromtimestamp(start)} and {datetime.fromtimestamp(end)}: {len(db.getAllEventByTime(1669476872, 1669477333))}")

    # print(db.getAlarmForState('rob1',600,'DOWN'))


if __name__ == "__main__":
    test()

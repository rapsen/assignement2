from sqlite3 import connect, Error
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
        self.SN = int(data['SN'])

    def __repr__(self) -> str:
        return f"Event: deviceId={self.deviceId} state={self.state} time={self.time} SN={self.SN}"

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

        try:
            self.c.execute(request)
        except Error as error:
            log.error(f" SQLite({error.args}) Request: {request}")

        if commit:
            self.connexion.commit()

        return self.c.fetchall()

    def __SELECT(self, table: str, element: tuple = ('*'), condition: str = str(True)) -> list:
        """ Private method to select element of the table with given condition """

        return self.execute(f"SELECT {element} FROM {table} WHERE {condition}")

    def __INSERT(self, table: str, values: tuple) -> list:
        """ Private method to insert in the table the values """

        self.execute(f"INSERT INTO {table} {TABLES[table]} VALUES {values}", commit=True)

    def __UPDATE(self, table: str, values: list, condition: str = str(True)) -> list[dict]:
        """ Private method to update ALL element of the table with the new values """

        update = ""

        for k, v in values.items():
            update += f"{k}='{v}', " if type(v) is str else f"{k}={v}, "

        self.execute(
            f"UPDATE {table} SET {update[:-2]} WHERE {condition}", commit=True)

    def SELECT_ALL_ROBOTS(self) -> list[Robot]:
        return [Robot(r) for r in self.__SELECT(ROBOT)]

    def SELECT_ALL_EVENTS(self) -> list[Event]:
        return [Event(d) for d in self.__SELECT(EVENT)]

    def SELECT_ALL_EVENT_BY_STATE(self, state: str) -> list[Event]:
        return [Event(d) for d in self.__SELECT(EVENT, condition=f"state == '{state}'")]

    def SELECT_ALL_EVENT_BY_ROBOT(self, deviceId: str) -> list[Event]:
        return [Event(d) for d in self.__SELECT(EVENT, condition=f"deviceId == '{deviceId}'")]

    def SELECT_ALL_EVENT_BETWEEN(self, start: int, end: int) -> list[Event]:
        return [Event(d) for d in self.__SELECT(EVENT, condition=f"time BETWEEN {start} AND {end}")]
    
    def SELECT_ALL_EVENT_BY_ROBOT_AND_STATE(self, deviceId: str, state: str) -> list[Event]:
        return [Event(d) for d in self.__SELECT(EVENT, condition=f"deviceId=='{deviceId}' AND state=='{state}'")]

    def getAllDeviceId(self) -> list:
        return [d["deviceId"] for d in self.__SELECT(EVENT, element="DISTINCT deviceId")]

    def getLastEventByRobot(self, deviceId: str) -> Event:
        return self.SELECT_ALL_EVENT_BY_ROBOT(deviceId)[-1]

    def getLastStateByRobot(self, deviceId: str):
        return self.__SELECT(EVENT, element="deviceId, state, time", condition=f"deviceId = '{deviceId}' ORDER BY time DESC;")

    def ADD_EVENT(self, event: Event):
        return self.__INSERT(EVENT, (event.deviceId, event.state, event.SN, event.time))

    def getRobEventBetweenTime(self, deviceId: str, start: int, end: int):
        return self.__SELECT(EVENT, element="deviceId, state, time", condition=f"deviceId = '{deviceId}' and time between '{start}' and '{end}' ORDER BY time ASC;")

    def getStateById(self, deviceId: str, state: str) -> list:
        return self.__SELECT(EVENT, element=f"id,time", condition=f"deviceId='{deviceId}' AND state='{state}'")

    def SELECT_ALL_ROBOT(self) -> list[Robot]:
        return [Robot(d) for d in self.__SELECT(ROBOT)]

    def SELECT_ROBOT(self, deviceId: int) -> Robot:
        return Robot(self.__SELECT(ROBOT, condition=f"{deviceId=}")[0])

    def ADD_ROBOT(self, robot: Robot) -> None:
        self.__INSERT(ROBOT, (robot.deviceId, robot.state, robot.time))

    def UPDATE_ROBOT(self, robot: Robot) -> None:
        deviceId = robot.deviceId
        self.__UPDATE(ROBOT, robot.__dict__, condition=f"{deviceId=}")


# Create instance of the database
database = Database()


def test():
    """ Test database operation """

    db = Database()

    r = {'deviceId': 'rob2', 'state': 'READY-PROCESSING-EXECUTING',
         'time': int(datetime.now().timestamp())}

    e = Event({'id': 4190, 'deviceId': 'rob2', 'state': 'READY-PROCESSING-EXECUTING',
               'SN': 17730, 'time': int(datetime.now().timestamp())})

    print("#####################  ROBOT  #########################")
    total_robot = db.SELECT_ALL_ROBOT()
    print(total_robot)
    print(f"Total Robot: {len(total_robot)}")
    for robot in total_robot:
        print(f"    {db.SELECT_ROBOT(robot.deviceId)}")

    print("#####################  EVENT  #########################")
    print(f"Total Event: {len(db.SELECT_ALL_EVENTS())}")
    print("     State:")
    for state in STATES:
        print(f"        {state}: {len(db.SELECT_ALL_EVENT_BY_ROBOT_STATE(state))}")
    print("     Robot:")
    for robot in total_robot:
        print(
            f"        {robot.deviceId}: {len(db.SELECT_ALL_EVENT_BY_ROBOT(robot.deviceId))}")

    print("     Robot and State:")
    print(f"        {EXECUTING}: {len(db.SELECT_ALL_EVENT_BY_ROBOT_AND_STATE('rob1', EXECUTING))}")



    start, end = 1669476872, 1669477333
    print(f"     Between {datetime.fromtimestamp(start)} and {datetime.fromtimestamp(end)}: {len(db.SELECT_ALL_EVENT_BETWEEN(1669476872, 1669477333))}")

    # print(db.getAlarmForState('rob1',600,'DOWN'))


if __name__ == "__main__":
    test()

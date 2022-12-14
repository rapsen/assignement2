from sqlite3 import connect, Error
from datetime import datetime
from time import mktime

from config import *


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Robot:
    """ Class to handle robots """

    def __init__(self, data: dict):
        self.deviceId = data['deviceId']
        self.state = data['state']
        self.time = data['time']
        self.convert()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.__dict__}"

    def convert(self):
        """ Convert the time to an integer timestamp if time is a string """
        if type(self.time) == str:
            self.time = int(mktime(datetime.strptime(
                self.time.replace(" ", "T")[0:19], "%Y-%m-%dT%H:%M:%S").timetuple()))


class Event(Robot):
    """" Class to handle events """

    def __init__(self, data: dict):
        super().__init__(data)
        self.sequenceNumber = int(data['sequenceNumber'])

    def robot(self) -> Robot:
        """ Return an Robot instance with event parameter """
        return Robot(self.__dict__)


class Database():
    """ Class to handle database """

    def __init__(self):
        self.__connexion = connect(DATABASE, check_same_thread=False)
        self.__connexion.row_factory = dict_factory
        self.__cursor = self.__connexion.cursor()

        self.create()

    def create(self):
        with open(DATABASE_SCRIPT, 'r') as db:
            script = db.read()

        self.__cursor.executescript(script)
        self.__connexion.commit()

    def execute(self, request: str, commit: bool = False) -> list:

        try:
            self.__cursor.execute(request)
        except Error as error:
            log.error(f" SQLite({error.args}) Request: {request}")

        if commit:
            self.__connexion.commit()

        return self.__cursor.fetchall()

    def __SELECT(self, table: str, element: tuple = ('*'), condition: str = str(True)) -> list:
        """ Private method to select element of the table with given condition """

        return self.execute(f"SELECT {element} FROM {table} WHERE {condition}")

    def __INSERT(self, table: str, values: tuple) -> list:
        """ Private method to insert in the table the values """

        self.execute(f"INSERT INTO {table} {TAB[table]} VALUES {values}", True)

    def __UPDATE(self, table: str, values: dict, c: str = str(True)) -> list[dict]:
        """ Private method to update ALL element of the table with the new values for given c"""

        update = ""

        for k, v in values.items():
            update += f"{k}='{v}', " if type(v) is str else f"{k}={v}, "

        self.execute(f"UPDATE {table} SET {update[:-2]} WHERE {c}", True)
        
    def SELECT_BETWEEN(self, deviceId: str, start: int, end: int, ) -> list[Event]:
        return [Event(d) for d in self.__SELECT(EVENT, condition=f"deviceID=='{deviceId}' AND time BETWEEN {start} AND {end}")]

    def SELECT_DISTINCT_STATE(self) -> list:
        return [d["state"] for d in self.__SELECT(EVENT, element="DISTINCT state")]

    def ADD_EVENT(self, event: Event):
        return self.__INSERT(EVENT, (event.deviceId, event.state, event.sequenceNumber, event.time))

    def SELECT_EVENT_BETWEEN(self, deviceId: str, start: int, end: int):
        return self.__SELECT(EVENT, element="deviceId, state, time", condition=f"deviceId = '{deviceId}' and time between '{start}' and '{end}' ORDER BY time ASC;")

    def SELECT_ALL_ROBOTS(self) -> list[Robot]:
        return [Robot(d) for d in self.__SELECT(ROBOT)]

    def SELECT_ROBOT(self, deviceId: int) -> Robot:
        return Robot(self.__SELECT(ROBOT, condition=f"{deviceId=}")[0])

    def ADD_ROBOT(self, robot: Robot) -> None:
        self.__INSERT(ROBOT, (robot.deviceId, robot.state, robot.time))

    def UPDATE_ROBOT(self, robot: Robot) -> None:
        deviceId = robot.deviceId
        self.__UPDATE(ROBOT, robot.__dict__, c=f"{deviceId=}")


# Create instance of the database
database = Database()

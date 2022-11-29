import sqlite3
from config import *
DATABASE = "database.db"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Model():
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
        #print(self.request)

        return self.execute()

    def getAllEvents(self) -> list:
        return self.__SELECT()

    def getAllEventByState(self, state: str) -> list:
        return self.__SELECT(condition=f"state == '{state}'")

    def getAllEventByRobot(self, deviceId: str) -> list:
        return self.__SELECT(condition=f"deviceId == '{deviceId}'")

    def getAllEventByTime(self, start: int, end: int) -> list:
        return self.__SELECT(condition=f"time BETWEEN {start} AND {end}")

    def getEventById(self, id: int):
        return self.__SELECT(condition=f"id == {id}")
    
    def getAllDeviceId(self):
        return self.__SELECT(element="DISTINCT deviceId")

        


model = Model()

# Test get methods

# print(model.getAllEvents())
# print(model.getAllEventByState(DOWN))
# print(model.getAllEventByRobot("rob1"))
# print(model.getAllEventByTime(1669476872, 1669477333))
# print(model.getEventById(3))
# print(model.getAllDeviceId())

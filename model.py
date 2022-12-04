from sqlite3 import connect
from datetime import datetime, timedelta
from time import mktime

from config import *
from database import database, Robot, Event


class Model():
    def __init__(self):
        # List to hold all the robots deviceId
        self.robots = [r.deviceId for r in self.getRobots()]

    def getRobots(self) -> list:
        return database.SELECT_ALL_ROBOT()

    def addEvent(self, event: Event):
        print("New event in db: ", event)
        database.ADD_EVENT(event)

    def last_event(self, id: str) -> Event:
        a = database.getLastEventByRobot(id).__dict__
        print(a)
        return a

    def handle(self, data: dict) -> Event:
        event = Event(data)
        database.ADD_EVENT(event)
        if event.deviceId in self.robots:
            database.UPDATE_ROBOT(event.robot())
        else:
            database.ADD_ROBOT(event.robot())
        return event

    def update(self, data: dict):
        # Update database
        data['time'] = iso2timestamp(data['time'])
        self.addEvent(Event(dict(data)))

    def getlaststate(self, deviceId: str):
        data = database.getLastStateByRobot(deviceId)[0]
        return data

    def getRobEffBetTime(self, deviceId: str, start: int, end: int):
        """ This function calculates KPIs and Mean Time -> returns dict"""
        list = database.getRobEventBetweenTime(deviceId, start, end)
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
        robot = database.SELECT_ALL_EVENT_BY_ROBOT(deviceId)
        EventsInAlarm = []

        for robotState in database.getStateById(deviceId, state):
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

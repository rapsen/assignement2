from sqlite3 import connect
from datetime import datetime
from time import mktime

from config import *
from database import database, Robot, Event


class Alarm():
    def __init__(self, state, start: int, end: int) -> None:
        self.state = state
        self.delta = end - start
        self.start = datetime.fromtimestamp(start)
        self.end = datetime.fromtimestamp(end)


class Model():
    def __init__(self):
        # List to hold all the robots deviceId
        self.robots = [r.deviceId for r in self.getRobots()]
        self.states = database.SELECT_DISTINCT_STATE()

    def getRobots(self) -> list[Robot]:
        return database.SELECT_ALL_ROBOTS()

    def addEvent(self, event: Event):
        print("New event in db: ", event)
        database.ADD_EVENT(event)

    def on_message(self, data: dict) -> Event:
        event = Event(data)
        database.ADD_EVENT(event)

        if event.deviceId in self.robots:
            robot = event.robot()
            database.UPDATE_ROBOT(robot)

        else:
            robot = Robot(data)
            database.ADD_ROBOT(robot)

        print(event)
        # self.monitor(event)
        return event

    def update(self, data: dict):
        # Update database
        # We store date as timestamp
        data['time'] = iso2epoch(data['time'])
        print(data)
        self.addEvent(Event(dict(data)))

    def getRobEffBetTime(self, deviceId: str, start: int, end: int):
        """ This function calculates KPIs and Mean Time -> returns dict"""
        list = database.SELECT_EVENT_BETWEEN(deviceId, start, end)
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
            if total_gathered_time:
                time_state = stateDict[rep]
                perc = round((time_state * 100) / total_gathered_time, 1)
                efficiency.update({rep: perc})

        total_fail_time = sum(infailure_times)
        mean_time = total_fail_time / \
            len(infailure_times) if len(infailure_times) != 0 else 0
        # efficiency.update({"MEAN": mean_time})
        # print("States:", efficiency)
        return efficiency, int(mean_time)

    def getAlarms(self, deviceId: str, start: str, end: str, state: str, trigger: int = 200) -> list[Alarm]:
        s, e = iso2epoch(start), iso2epoch(end)
        events = database.SELECT_BETWEEN(deviceId, s, e)
        alarms = []

        if events:
            before = events[0]
            alarm = None

            for now in events:
                if now.state == state:
                    delta = now.time - before.time  # Current time - previous time
                    if delta > trigger:
                        alarm = Alarm(now.state, before.time, now.time)
                else:
                    before = now
                    if alarm is not None:
                        alarms.append(alarm)
                        alarm = None
        return {"alarms": alarms, "start": start, "end": end}


def iso2epoch(time: str) -> int:
    """ Return the give datetime as an ISO 8601 string """
    if len(time) < 26:
        time = time + ":00.0"  # Add padings for the seconds
    return int(mktime(datetime.strptime(time[0:26], "%Y-%m-%dT%H:%M:%S.%f").timetuple()))


def epoch2iso(time: int = None) -> str:
    """ Return the given timestamp as a stringdatetime ISO 8651 formatted for the HTML datetime tags """
    return datetime.now(time).strftime("%Y-%m-%dT%H:%M")


# Create instance of the model
model = Model()

if __name__ == "__main__":
    import sys
    trigger = int(sys.argv[1])
    print(len(model.getAlarms("rob1", DOWN, trigger)))

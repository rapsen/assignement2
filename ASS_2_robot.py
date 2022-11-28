import ASS_2_SQLdb

sql = ASS_2_SQLdb

def time_change(time):
    "2022-11-23T11:10:55.556696728Z"
    "012345678911234567892123456789"
    yy = time[0:4]
    mm = time[5:7]
    dd = time[8:10]
    hh = time[11:13]
    min = time[14:16]
    sec = time[17:19]
    msec = time[20:22]
    time = f"{dd}.{mm}.{yy} {hh}:{min}:{sec}.{msec}"
    return time

class Robot:
    def __init__(self, robotID):
        self.robotID = robotID
        self.state = str
        self.lastTimeConnected = str
        self.efficiency = dict

    def get_rob_name(self) -> str:
        return self.robotID

    def get_rob_state(self) -> str:
        st = sql.get_realtime_robot_state(self.robotID)
        self.state = st["state"]
        return self.state

    def get_rob_lastTimeCon(self) -> str:
        tm = sql.get_realtime_robot_state(self.robotID)
        self.lastTimeConnected = tm["time"]
        return self.lastTimeConnected

    def get_rob_efficiency(self, start, end) -> dict:
        self.efficiency = sql.get_data_by_time(self.robotID, start, end)
        return self.efficiency

#rob2 = Robot("rob1")
#try_state = Robot.get_rob_state(rob2)
#print(f"{rob2.robotID} is in state:{try_state}")

#try_efficiency = Robot.get_rob_efficiency(rob2, "23.11.2022 22:20", "23.11.2022 22:50")
#print(f"Efficiency of {rob2.robotID} is {try_efficiency}")
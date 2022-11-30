import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('robotDB4.db', check_same_thread=False)
conn.row_factory = dict_factory
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS robot (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        deviceId text, 
                        state text, 
                        time text, 
                        sequenceNumber integer
                        );""")


def handle_mess(payload):
    print(f"Got message {payload}")
    robotID = payload["deviceId"]
    state = payload["state"]
    time = payload["time"]
    sequenceNr = int(payload["sequenceNumber"])
    insert_robot(robotID, state, time, sequenceNr)
    return payload

def transfer_to_sec(time):
    "23.11.2022 20:47:41.68"
    "0123456789112345678921"
    hh = int(time[11:13])
    min = int(time[14:16])
    sec = float(time[17:21])
    total_sec = float(hh * 3600 + min * 60 + sec)
    return round(total_sec, 2)

def insert_robot(robotID, state, time, sequenceNr):
    with conn:
        c.execute("INSERT INTO robot VALUES (:id, :deviceId, :state, :time, :sequenceNumber)",
                  {'id': None, 'deviceId': robotID, 'state': state, 'time': time, 'sequenceNumber': sequenceNr})

#READ
def get_all_robots():
    sqlSt="SELECT * FROM robot WHERE 1"
    c.execute(sqlSt)
    return c.fetchall()

#READ
def get_realtime_robot_state(robotID):
    # if robotID not in ValidRobotID:
    sqlSt=f"SELECT * FROM robot WHERE deviceId = '{robotID}' ORDER BY time DESC;"
    c.execute(sqlSt)
    list = c.fetchall()
    dict = list[0]
    state = dict["state"]
    time = dict["time"]
    result = {"state": state, "time": time}
    return result

#READ
def get_data_by_time(robotID, start, end):
    sqlSt=f"SELECT state, time FROM robot WHERE deviceId = '{robotID}' and time between " \
          f"'{start}' and '{end}' ORDER BY time ASC;"
    c.execute(sqlSt)

    list = c.fetchall()
    stateDict = {}
    efficiency = {}
    up_time = 0
    down_time = 0
    infailure_times = []
    for rep in range(len(list) - 1):
        start_dict = list[rep]
        end_dict = list[rep + 1]
        start_time = transfer_to_sec(start_dict["time"])
        end_time = transfer_to_sec(end_dict["time"])
        robot_state = start_dict["state"]

        # When failure is repaired
        if start_dict["state"] == "DOWN" and end_dict["state"] != "DOWN":
            up_time = end_time
        # When failure appear
        elif start_dict["state"] != "DOWN" and end_dict[
            "state"] == "DOWN" and up_time != 0:
            down_time = end_time

        if up_time != 0 and down_time != 0:
            infailure_time = round(down_time - up_time, 1)
            infailure_times.append(infailure_time)
            up_time = 0
            down_time = 0

        if robot_state not in stateDict:
            stateDict.update({robot_state: 0})
        if start_time > end_time:
            total_time = round(((24 * 3600) - start_time) + end_time, 1)
        else:
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

    return efficiency

# robot = get_realtime_robot_state("rob1")
# print(robot)
#
# times = get_data_by_time("rob1", "26.11.2022 17:25:30", "26.11.2022 22:50")
# print(times)
#
# conn.close()

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
    time_RIS = 0
    time_RPE = 0
    time_DOWN = 0
    for rep in range(len(list)-1):
        start_dict = list[rep]
        end_dict = list[rep+1]
        start_time = transfer_to_sec(start_dict["time"])
        end_time = transfer_to_sec(end_dict["time"])
        if start_time > end_time:
            total_time = round(((24*3600)-start_time) + end_time, 1)
        else:
            total_time = round(end_time-start_time, 1)
        #print(f"State {start_dict['state']} Start:{start_time} End:{end_time} Total:{total_time}")

        if start_dict["state"]=="READY-IDLE-STARVED":
            time_RIS += total_time
        elif start_dict["state"]=="READY-PROCESSING-EXECUTING":
            time_RPE += total_time
        elif start_dict["state"]=="DOWN":
            time_DOWN += total_time
    total_gathered_time = time_RIS + time_RPE + time_DOWN
    perc_RIS = round((time_RIS * 100) / total_gathered_time,1)
    perc_RPE = round((time_RPE * 100) / total_gathered_time,1)
    perc_DOWN = round((time_DOWN * 100) / total_gathered_time,1)

    efficiency = {"READY-IDLE-STARVED": perc_RIS , "READY-PROCESSING-EXECUTING":
        perc_RPE , "DOWN": perc_DOWN}
    #print(f"{robotID} RIS:{perc_RIS}% RPE:{perc_RPE}% DOWN:{perc_DOWN}%")

    return efficiency

#robot = get_realtime_robot_state("rob1")
#print(robot)

#times = get_data_by_time("rob1", "23.11.2022 22:20", "23.11.2022 22:50")
#print(times)

#conn.close()

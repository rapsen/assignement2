import logging as log
from colorlog import ColoredFormatter

LOG_LEVEL = log.DEBUG
LOGFORMAT = "[%(asctime)-s] [%(log_color)s%(levelname)-s%(reset)s] [%(module)s] %(log_color)s%(message)s%(reset)s"
log.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT, "%Y-%m-%d %H:%M:%S")
stream = log.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = log.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)


BROKER_HOSTNAME = "broker.mqttdashboard.com"
BROKER_PORT = 1883
MQTT_TOPIC = "ii22/telemetry/#"

# Alarms trigers
ALARM_DOWN = 100
ALARM_IDLE = 1000

DATABASE = "data/database.db"
DATABASE_SCRIPT = "data/database.sql"
# Description of the database
EVENT = "Event"
ROBOT = "Robot"
TABLES = {
    EVENT: ("deviceId", "state", "SN", "time"),
    ROBOT: ("deviceId", "state", "time")
}

# Possible States

STARVED = "READY-IDLE-STARVED"
BLOCKED = "READY-IDLE-BLOCKED"
EXECUTING = "READY-PROCESSING-EXECUTING"
PROCESSING = "processing"
ACTIVE = "READY-PROCESSING-ACTIVE"
SETUP = "SETUP"
DOWN = "DOWN"
OFF = "OFF"
STATES = [STARVED, BLOCKED, EXECUTING, PROCESSING, ACTIVE, SETUP, DOWN, OFF]

ISO_TIME = "%Y-%m-%dT%H:%M:%S"

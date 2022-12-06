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

CONFIG = {
    'MQTT_BROKER_URL': "broker.mqttdashboard.com",
    'MQTT_BROKER_PORT': 1883,
    'MQTT_KEEPALIVE': 60,
    'MQTT_TLS_ENABLED': False
}

MQTT_TOPIC = "ii22/telemetry/#"
DATABASE = "data/database.db"
DATABASE_SCRIPT = "data/database.sql"

# Description of the database
EVENT = "Event"
ROBOT = "Robot"
ALARM_TRIGGERS = 'Alarms'
TAB = {
    EVENT: ("deviceId", "state", "SN", "time"),
    ROBOT: ("deviceId", "state", "time", "trigger"),
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

ALARM_STATES = [DOWN, STARVED, BLOCKED, SETUP, OFF]

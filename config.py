from logging.config import dictConfig
import logging as log

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] [%(module)s:%(lineno)s] %(message)s',
        'datefmt': '%d/%m/%y %H:%M:%S'
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default',
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

BROKER_HOSTNAME = "broker.mqttdashboard.com"
BROKER_PORT = 1883
MQTT_TOPIC = "ii22/telemetry/#"

DATABASE = "data/database.db"
DATABASE_SCRIPT = "data/database.sql"
# Description of the database 
EVENT = "Event"
ROBOT = "Robot"
TABLES = {
    EVENT: ("deviceId", "state", "sequenceNumber", "time"),
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
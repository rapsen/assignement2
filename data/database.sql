CREATE TABLE IF NOT EXISTS "Event" (
    "id"	INTEGER,
    "deviceId"	TEXT,
    "state"	TEXT,
    "sequenceNumber"	INTEGER,
    "time"	INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT));

CREATE TABLE IF NOT EXISTS "Robot" (
    "id"	INTEGER NOT NULL UNIQUE,
    "deviceId"	TEXT,
    "state"	TEXT,
    "time"	INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT));
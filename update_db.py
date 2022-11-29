import sqlite3
from model import Model
import time
import datetime

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


bd = Model()

events = bd.getAllEvents()

print(events)

for event in events:
    print(event)
    t = event["str_time"]
    
    new_t = int(time.mktime(datetime.datetime.strptime(t, "%d.%m.%Y %H:%M:%S.%f").timetuple()))
    print(new_t)
    
    bd.request = f"UPDATE Event SET time = {new_t} WHERE id == {event['id']}"
    
    print(bd.request)
    
    print(bd.execute())
    
    
bd.connexion.commit()
    
    
import time
import sqlite3

DB_URL = "/home/pi/.action-scheduler"

conn = sqlite3.connect(DB_URL)
cursor = conn.cursor()


def init():
    sql_create_events_table = """ CREATE TABLE IF NOT EXISTS events (
                                        uuid integer PRIMARY KEY,
                                        event_time integer NOT NULL,
                                        name TEXT
                                    ); """

    cursor.execute(sql_create_events_table)


def create_event(event_time, name=None):
    sql_insert_event_without_name = """ INSERT INTO events (event_time, name)
                                        VALUES (?, NULL);"""

    sql_insert_event_with_name = """ INSERT INTO events (event_time, name)
                                        VALUES (?, ?);"""

    if name is None:
        try:
            cursor.execute(sql_insert_event_without_name, [event_time])
            conn.commit()
        except Exception as e:
            print(e)

    else:
        try:
            cursor.execute(sql_insert_event_with_name, [event_time, name])
            conn.commit()
        except Exception as e:
            print(e)


def get_due_events():
    event_time = time.time()
    sql_select_due_event = """SELECT uuid, name
                              FROM events
                              WHERE event_time < ?;"""

    cursor.execute(sql_select_due_event, [event_time])

    return cursor.fetchall()


def delete_event(uuid):
    sql_delete_event = """DELETE FROM events WHERE uuid=?"""

    cursor.execute(sql_delete_event, [uuid])
    conn.commit()

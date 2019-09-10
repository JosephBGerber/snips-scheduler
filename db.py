import time
import sqlite3

DB_URL = "/var/lib/snips/snips-scheduler/action-scheduler.sqlite"


class Database:

    def __init__(self):

        self.conn = sqlite3.connect(DB_URL)
        self.cursor = self.conn.cursor()

        sql_create_events_table = """ CREATE TABLE IF NOT EXISTS events (
                                            uuid integer PRIMARY KEY,
                                            event_time integer NOT NULL,
                                            name TEXT
                                        ); """

        self.cursor.execute(sql_create_events_table)
        self.conn.commit()

    def create_event(self, event_time, name=None):
        sql_insert_event_without_name = """ INSERT INTO events (event_time, name)
                                            VALUES (?, NULL);"""

        sql_insert_event_with_name = """ INSERT INTO events (event_time, name)
                                            VALUES (?, ?);"""

        if name is None:
            self.cursor.execute(sql_insert_event_without_name, [event_time])
            self.conn.commit()

        else:
            self.cursor.execute(sql_insert_event_with_name, [event_time, name])
            self.conn.commit()

    def get_due_events(self):
        event_time = time.time()
        sql_select_due_event = """SELECT uuid, name
                                  FROM events
                                  WHERE event_time < ?;"""

        self.cursor.execute(sql_select_due_event, [event_time])

        return self.cursor.fetchall()

    def delete_event(self, uuid):
        sql_delete_event = """DELETE FROM events WHERE uuid=?"""

        self.cursor.execute(sql_delete_event, [uuid])
        self.conn.commit()

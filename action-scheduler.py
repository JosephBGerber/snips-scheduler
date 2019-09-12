#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict
import time
import threading
from hermes_python.hermes import Hermes, IntentMessage
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import db


def set_reminder_callback(hermes, intent_message):
    # type: (Hermes, IntentMessage) -> None

    handle = db.Database()

    event_time_str = intent_message.slots["time"].first().value[:-7]  # remove timezone information for the time value
    event_time_struct = time.strptime(event_time_str, "%Y-%m-%d %H:%M:%S")  # parse the str time into a time.time_struct
    event_time = time.mktime(event_time_struct)  # store the resulting epoch time

    if len(intent_message.slots) == 1:
        uuid = handle.create_event(event_time)
        message = "Reminder created at %I %M %p with an I D of {}".format(uuid)
        message = time.strftime(message, event_time_struct)
        hermes.publish_end_session(intent_message.session_id, message)
        return

    if len(intent_message.slots) == 2:
        event = intent_message.slots["event"].first().value

        uuid = handle.create_event(event_time)
        message = "Reminder created to {} at %I %M %p with an I D of {}".format(
            event,
            uuid)
        message = time.strftime(message, event_time_struct)
        hermes.publish_end_session(intent_message.session_id, message)
        return


def delete_reminder_callback(hermes, intent_message):
    # type: (Hermes, IntentMessage) -> None

    uuid = intent_message.slots["uuid"].first().value

    handle = db.Database()
    handle.delete_event(uuid)
    message = "Reminder with I D {} deleted".format(uuid)
    hermes.publish_end_session(intent_message.session_id, message)


def event_thread(hermes):
    # type: (Hermes) -> None

    handle = db.Database()

    while True:
        time.sleep(1)
        for (uuid, name) in handle.get_due_events():
            if name is None:
                hermes.publish_start_session_notification("default", "This is a reminder to do your stuff.", None)
                handle.delete_event(uuid)
            else:
                message = "This is a reminder to {}".format(name)
                hermes.publish_start_session_notification("default", message, None)
                handle.delete_event(uuid)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        threading.Thread(target=event_thread, args=(h,)).start()
        h.subscribe_intent("JosephBGerber:SetReminder", set_reminder_callback)\
            .subscribe_intent("JosephBGerber:DeleteReminder", delete_reminder_callback)\
            .start()

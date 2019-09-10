#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict
import configparser
import time
import threading
from hermes_python.hermes import Hermes, IntentMessage
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import db

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"


class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name: option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()


def subscribe_intent_callback(hermes, intent_message):
    # type: (Hermes, IntentMessage) -> None
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intent_message, conf)


def action_wrapper(hermes, intent_message, conf):
    # type: (Hermes, IntentMessage, Dict) -> None

    handle = db.Database()

    event_time = intent_message.slots["time"].first().value[:-7]
    event_time = time.strptime(event_time, "%Y-%m-%d %H:%M:%S")
    event_time = time.mktime(event_time)
    
    if len(intent_message.slots) == 1:
        handle.create_event(event_time)
        hermes.publish_end_session(intent_message.session_id, "I'll remind you!")
        return

    if len(intent_message.slots) == 2:
        event = intent_message.slots["event"].first().value

        handle.create_event(event_time, event)
        hermes.publish_end_session(intent_message.session_id, "I'll remind you to {}".format(event))
        return


def event_thread(hermes):
    # type: (Hermes) -> None

    handle = db.Database()

    while True:
        time.sleep(1)
        for (uuid, name) in handle.get_due_events():
            if name is None:
                hermes.publish_start_session_notification("default", "This is a reminder to do your shit.", None)
                handle.delete_event(uuid)
            else:
                message = "This is a reminder to {}".format(name)
                hermes.publish_start_session_notification("default", message, None)
                handle.delete_event(uuid)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        threading.Thread(target=event_thread, args=(h,)).start()
        h.subscribe_intent("JosephBGerber:SetReminder", subscribe_intent_callback).start()

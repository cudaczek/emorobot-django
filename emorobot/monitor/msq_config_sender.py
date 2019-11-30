import paho.mqtt.client as mqtt
import threading
import json
from enum import Enum

class UpdateType(Enum):
    EMOTIONS_ONLY = 0
    RAW_ONLY = 1
    ALL = 2

class NetworkType(Enum):
    AUDIO = 0
    VIDEO = 1


class ConfigSender:
    def __init__(self):
        with open('communication.json', 'r') as json_file:
            config = json.load(json_file)
            self.config_topic = config["BASE_TOPIC"] + config["CONFIGURATION_TOPIC_SUFFIX"]
            self.client = mqtt.Client()
            self.client.connect(config["BROKER_IP_OR_NAME"], int(config["BROKER_PORT"]), 60)

    def send_config(self,
                                  update_type: UpdateType=None, 
                                  update_cycle_on: bool=None, 
                                  stop: NetworkType=None,
                                  start: NetworkType=None,
                                  tick_length: int=None):
        config = {}
        if update_cycle_on:
            config['UPDATE_CYCLE_ON'] = update_cycle_on
        # add other parameters to json if applicable
        self.client.publish(self.config_topic, json.dumps(config))
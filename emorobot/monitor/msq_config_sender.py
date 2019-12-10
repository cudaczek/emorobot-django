import paho.mqtt.client as mqtt
import threading
import json
from enum import Enum

class UpdateType(Enum):
    EMOTIONS_ONLY = 0
    RAW_ONLY = 1
    ALL = 2

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) is UpdateType:
            return str(obj.value)
        return json.JSONEncoder.default(self, obj)

class ConfigSender:
    def __init__(self):
        try:
            with open('communication.json', 'r') as json_file:
                config = json.load(json_file)
                self.config_topic = config["BASE_TOPIC"] + config["CONFIGURATION_TOPIC_SUFFIX"]
                self.client = mqtt.Client("jaRobot")
                self.client.connect(config["BROKER_IP_OR_NAME"], int(config["BROKER_PORT"]))
                threading.Thread(target=lambda: self.client.loop_forever()).start()
        except Exception as es:
            print("init ", str(es))

    def send_config(self,
                                  update_type: UpdateType=None, 
                                  update_cycle_on: bool=None, 
                                  tick_length: int=None):
        try:
            config = {}
            if update_cycle_on is not None:
                config['UPDATE_CYCLE_ON'] = update_cycle_on
            if update_type is not None:
                config['UPDATE_TYPE'] = update_type
            if tick_length is not None:
                config['TICK_LENGTH'] = tick_length
            self.client.publish(self.config_topic, json.dumps(config, cls=EnumEncoder), qos=2)
            print("sent config message " + json.dumps(config, cls=EnumEncoder))
            print("topic: "+self.config_topic)
        except Exception as es:
            print("send_config error ", str(es))

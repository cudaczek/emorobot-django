import json
import threading

import paho.mqtt.client as mqtt


class MessageReceiver:
    def __init__(self):
        with open('communication.json', 'r') as json_file:
            config = json.load(json_file)
            self.update_topic = config["BASE_TOPIC"] + config["UPDATE_TOPIC_SUFFIX"]
            self.client = mqtt.Client()
            self.client.on_connect = lambda client, userdata, flags, rc: self.connect_callback(
                self.update_topic, rc)
            self.client.on_message = lambda client, userdata, msg: self.message_callback(msg)
            self.client.connect(config["BROKER_IP_OR_NAME"], int(config["BROKER_PORT"]), 60)
            threading.Thread(target=lambda: self.client.loop_forever()).start()
            print("finished constructor")
            self.emotion_data = {"Speech-Emotion-Analyzer": {"a": 1.0}, "video": {"a": 1.0}}
            self.raw_data = {"Speech-Emotion-Analyzer": b'', "video": b''}
            self.types={}

    def connect_callback(self, topic, rc):
        self.client.subscribe(topic)

    def message_callback(self, msg):
        import json
        message = json.loads(msg.payload)
        # print(message)
        name = message["network"]
        self.types[name]=message["type"]
        if "emotion_data" in message:
            self.emotion_data[name] = message["emotion_data"]
            # print(self.emotion_data[name])
        if "raw_data" in message:
            import base64
            self.raw_data[name] = base64.b64decode(message["raw_data"])
            # print(self.raw_data[name])

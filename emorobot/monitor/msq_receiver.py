import json
import threading

import paho.mqtt.client as mqtt


class MessageReceiver:
    def __init__(self, data_saver):
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
            self.emotion_data = {"audio": {"a": 1.0}, "video": {"a": 1.0}}
            self.raw_data = {"audio": b'', "video": b''}
            self.timestamp_raw = {"audio": "", "video": ""}
            self.timestamp_emo = {"audio": "", "video": ""}
            self.names = {"video": "", "audio": ""}
        self.data_sever = data_saver

    def connect_callback(self, topic, rc):
        self.client.subscribe(topic)

    def message_callback(self, msg):
        print(msg.payload[:100])
        import json
        message = json.loads(msg.payload)
        # print(message)
        # print("got_message")
        type = message["type"]
        name = message["network"]
        if name != self.names[type]:
            self.names[type] = name
            self.data_sever.update_nn_name(name, type)
        if "emotion_data" in message:
            self.timestamp_emo[type] = message["timestamp"]
            self.emotion_data[type] = message["emotion_data"]
            self.data_sever.save_emotions(type, self.emotion_data[type], message["timestamp"])
            # print(self.emotion_data[name])k
        if "raw_data" in message:
            self.timestamp_raw[type] = message["timestamp"]
            import base64
            self.raw_data[type] = base64.b64decode(message["raw_data"])
            self.data_sever.save_raw_data(type, self.raw_data[type], message["timestamp"])
            # print(self.raw_data[name])

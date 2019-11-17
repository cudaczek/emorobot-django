import io
import json
import os
import threading
from datetime import datetime

import paho.mqtt.client as mqtt
from PIL import Image


class MessageReceiver:
    def __init__(self):
        with open('communication.json', 'r') as json_file:
            config = json.load(json_file)
            self.update_topic = config["BASE_TOPIC"] + config["UPDATE_TOPIC_SUFFIX"]
            self.client = mqtt.Client()
            self.client.on_connect = lambda client, userdata, flags, rc: self.connect_callback(self.update_topic, rc)
            self.client.on_message = lambda client, userdata, msg: self.message_callback(msg)
            self.client.connect(config["BROKER_IP_OR_NAME"], int(config["BROKER_PORT"]), 60)
            threading.Thread(target=lambda: self.client.loop_forever()).start()
            print("finished constructor")
            self.emotion_data = {"audio": {"a": 1.0}, "video": {"a": 1.0}}
            self.raw_data = {"audio": b'', "video": b''}
            self.save_picture = False
            self.directory_path = None

    def connect_callback(self, topic, rc):
        self.client.subscribe(topic)

    def message_callback(self, msg):
        import json
        message = json.loads(msg.payload)
        # print(message)
        name = message["network"]
        if "emotion_data" in message:
            self.emotion_data[name] = message["emotion_data"]
        if "raw_data" in message:
            import base64
            self.raw_data[name] = base64.b64decode(message["raw_data"])
            if name == "video" and self.save_picture:
                self.do_save_picture(self.raw_data[name])

    def start_saving_pictures(self, directory_path):
        print("Start")
        self.save_picture = True
        self.directory_path = directory_path

    def stop_saving_pictures(self):
        self.save_picture = False

    def do_save_picture(self, bytes):
        image = Image.open(io.BytesIO(bytes))
        timestamp = datetime.timestamp(datetime.now())
        file_path = os.path.join(self.directory_path, str(timestamp))
        image.save(file_path, "PNG")

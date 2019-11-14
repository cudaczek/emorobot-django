import paho.mqtt.client as mqtt
import threading
import json


class MessageReceiver:
    def __init__(self):
        with open('communication.json', 'r') as json_file:
            config = json.load(json_file)
            self.update_topic=config["BASE_TOPIC"] + config["UPDATE_TOPIC_SUFFIX"]
            self.client = mqtt.Client()
            self.client.on_connect = lambda client, userdata, flags, rc : self.connect_callback(self.update_topic, rc)
            self.client.on_message = lambda client, userdata, msg : self.message_callback(msg)
            self.client.connect(config["BROKER_IP_OR_NAME"], int(config["BROKER_PORT"]), 60) 
            threading.Thread(target = lambda : self.client.loop_forever()).start()
            print("finished constructor")
            self.messages={"audio":"{\"emotion-data\":{\"a\":1.3}}", "video":"{\"emotion-data\":{\"a\":1.3}}"}

    def connect_callback(self, topic, rc):
        self.client.subscribe(topic)

    def message_callback(self, msg):
        print(msg.payload)
        import json
        name = json.loads(msg.payload)["network"]
        self.messages[name] = msg.payload.decode('utf-8')


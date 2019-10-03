import paho.mqtt.client as mqtt
import threading


class MessageReceiver:
    def __init__(self, topic, address):
        self.topic=topic
        self.address=address
        self.client = mqtt.Client()
        self.client.on_connect = lambda client, userdata, flags, rc : self.connect_callback(topic, rc)
        self.client.on_message = lambda client, userdata, msg : self.message_callback(msg)
        self.client.connect("broker.hivemq.com", 1883, 60) 
        threading.Thread(target = lambda : self.client.loop_forever()).start()
        print("finished constructor")
        self.message=":(-"

    def connect_callback(self, topic, rc):
        self.client.subscribe(topic)

    def message_callback(self, msg):
        print(msg.payload)
        self.message = msg.payload.decode('utf-8')


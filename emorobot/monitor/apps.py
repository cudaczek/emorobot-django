from django.apps import AppConfig
from . import msq_receiver


class MonitorConfig(AppConfig):
    name = 'monitor'
    def ready(self):
        self.receiver=msq_receiver.MessageReceiver("emorobo.mqtt.example.topic", "broker.hivemq.com:1883")

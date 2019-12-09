from django.apps import AppConfig
from . import msq_receiver, msq_config_sender


class MonitorConfig(AppConfig):
    name = 'monitor'
    def ready(self):
        self.receiver = msq_receiver.MessageReceiver()
        self.config_sender = msq_config_sender.ConfigSender()

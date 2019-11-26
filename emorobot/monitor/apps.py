from django.apps import AppConfig

from . import data_saver
from . import msq_receiver


class MonitorConfig(AppConfig):
    name = 'monitor'

    def ready(self):
        self.data_saver = data_saver.DataSaver()
        self.receiver = msq_receiver.MessageReceiver(self.data_saver)

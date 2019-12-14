from django.apps import AppConfig

from .classifiers import audio_classifier, video_classifier
from . import data_saver
from . import msq_receiver, msq_config_sender


class MonitorConfig(AppConfig):
    name = 'monitor'

    def ready(self):
        self.audio_classifier = audio_classifier.AudioRawDataClassifier("Emotion_Voice_Detection_Model")
        self.video_classifier = video_classifier.VideoRawDataClassifier("Emotion_Video_Detection_Model")
        self.data_saver = data_saver.DataSaver(self.video_classifier, self.audio_classifier)
        self.receiver = msq_receiver.MessageReceiver(self.data_saver)
        self.config_sender = msq_config_sender.ConfigSender()

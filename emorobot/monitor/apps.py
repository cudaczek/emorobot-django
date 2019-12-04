from django.apps import AppConfig

from .predictors import audio_predictor, video_predictior
from . import data_saver
from . import msq_receiver


class MonitorConfig(AppConfig):
    name = 'monitor'

    def ready(self):
        self.audio_predictor = audio_predictor.AudioRawDataPredictor("Emotion_Voice_Detection_Model")
        self.video_predictor = video_predictior.VideoRawDataPredictor("Emotion_Video_Detection_Model")
        self.data_saver = data_saver.DataSaver(self.video_predictor, self.audio_predictor)
        self.receiver = msq_receiver.MessageReceiver(self.data_saver)

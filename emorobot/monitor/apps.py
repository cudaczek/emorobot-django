from django.apps import AppConfig

from . import audio_predictor
from . import msq_receiver
from . import video_nn_predictior


class MonitorConfig(AppConfig):
    name = 'monitor'

    def ready(self):
        self.audio_predictor = audio_predictor.AudioRawDataPredictor("Emotion_Voice_Detection_Model")
        self.video_predictor = video_nn_predictior.VideoRawDataPredictor("Emotion_Video_Detection_Model")
        self.receiver = msq_receiver.MessageReceiver()

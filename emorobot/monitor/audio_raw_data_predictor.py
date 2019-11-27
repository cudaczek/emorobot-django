import struct
import numpy as np

from .nn_evaluator import NeuralNetEvaluator


class AudioRawDataPredictor:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def predict(self, nn_name):
        audio_predictions = None
        audio_labels = None
        if self.raw_data != b'':
            count = int(len(self.raw_data) / 4)
            floats = struct.unpack(">" + ('f' * count), self.raw_data)
            filename = nn_name
            neural_net = NeuralNetEvaluator(file_name=filename, sample_rate=44100)
            audio_predictions = neural_net.predict(np.array(floats))
            audio_predictions = [pred.item() for pred in audio_predictions[0]]
            audio_labels = neural_net.names
        return audio_predictions, audio_labels

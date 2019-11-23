import struct
import numpy as np

from .nn_evaluator import NeuralNetEvaluator


class AudioRawDataPredictor:
    def __init__(self, filename):
        self.neural_net = NeuralNetEvaluator(file_name=filename, sample_rate=44100)

    def predict(self, raw_data):
        audio_predictions = None
        audio_labels = None
        if raw_data != b'':
            count = int(len(raw_data) / 4)
            floats = struct.unpack(">" + ('f' * count), raw_data)
            audio_predictions = self.neural_net.predict(np.array(floats))
            audio_predictions = [pred.item() for pred in audio_predictions[0]]
            audio_labels = self.neural_net.names
        return audio_predictions, audio_labels


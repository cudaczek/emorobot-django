import json
import struct

import keras
import librosa
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import model_from_json


class AudioRawDataPredictor:
    def __init__(self, filename):
        self.neural_net = AudioNeuralNetEvaluator(file_name=filename, sample_rate=44100)

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

    def grouped_predict(self, raw_data):
        if raw_data != b'':
            audio_predictions, audio_labels = self.predict(raw_data)
            return self.group(audio_predictions, audio_labels)
        else:
            return None, None

    def group(self, predictions, labels):
        groups_names = self.neural_net.grouped_emotions.keys()
        groups = self.neural_net.grouped_emotions
        grouped_emotions = dict()
        for group_name in groups_names:
            grouped_emotions.update({group_name: 0.0})
        grouped_emotions.update({"other": 0.0})
        for pred, label in zip(predictions, labels):
            added = False
            for group_name in groups_names:
                if label in groups[group_name]:
                    grouped_emotions[group_name] += pred
                    added = True
            if not added:
                grouped_emotions["other"] += pred
        return grouped_emotions.values(), grouped_emotions.keys()


class AudioNeuralNetEvaluator:

    def __init__(self, file_name, sample_rate):
        self.graph = tf.get_default_graph()
        self.file_name = file_name
        self.model = self.load_model()
        self.sample_rate = sample_rate

    def load_model(self):
        self.names = []
        with open('resources/' + self.file_name + '_info.json') as json_file:
            model_infos = json.load(json_file)
            model_path = model_infos["AUDIO_MODEL"]
            model_weights = model_infos["AUDIO_MODEL_WEIGHTS"]
            self.names = model_infos["names"]
            if "GROUPED_EMOTIONS" in model_infos.keys():
                self.grouped_emotions = model_infos["GROUPED_EMOTIONS"]
            else:
                self.grouped_emotions = self.load_global_emotions()
        json_file = open('resources/' + model_path, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights("resources/" + model_weights)
        opt = keras.optimizers.rmsprop(lr=0.00001, decay=1e-6)
        loaded_model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
        print("Loaded model from disk")
        return loaded_model

    def load_global_emotions(self):
        with open('resources/emotions_dict.json') as json_file:
            emotions = json.load(json_file)
        return emotions

    def predict(self, data):
        with self.graph.as_default():
            twodim = self.preprocess(data, self.sample_rate)
            predictions = self.model.predict(twodim)
        return predictions

    def preprocess(self, data, sample_rate):
        sample_rate = np.array(sample_rate)
        mfccs = np.mean(librosa.feature.mfcc(y=data,
                                             sr=sample_rate,
                                             n_mfcc=13, hop_length=205),
                        axis=0)
        livedf2 = pd.DataFrame(data=mfccs)
        livedf2 = livedf2.stack().to_frame().T
        return np.expand_dims(livedf2, axis=2)

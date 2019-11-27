import tensorflow as tf
import keras
import pandas as pd
import librosa
import numpy as np
import json

from keras.models import model_from_json


class NeuralNetEvaluator:

    def __init__(self, file_name, sample_rate):
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
        json_file = open('resources/' + model_path, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights("resources/" + model_weights)
        opt = keras.optimizers.rmsprop(lr=0.00001, decay=1e-6)
        loaded_model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
        print("Loaded model from disk")
        return loaded_model

    def predict(self, data):
        twodim = self.preprocess(data, self.sample_rate)
        preds = self.model.predict(twodim)
        return preds

    def preprocess(self, data, sample_rate):
        sample_rate = np.array(sample_rate)
        mfccs = np.mean(librosa.feature.mfcc(y=data,
                                             sr=sample_rate,
                                             n_mfcc=13, hop_length=205),
                        axis=0)
        livedf2 = pd.DataFrame(data=mfccs)
        livedf2 = livedf2.stack().to_frame().T
        return np.expand_dims(livedf2, axis=2)

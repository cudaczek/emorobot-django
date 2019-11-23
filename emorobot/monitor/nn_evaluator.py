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
        json_file = open('resources/model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights("resources/Emotion_Voice_Detection_Model.h5")
        print("Loaded model from disk")
        return loaded_model

    def predict(self, data):
        self.preprocess(data, self.sample_rate)
        return self.model

    def preprocess(self, data, sample_rate):
        sample_rate = np.array(sample_rate)
        mfccs = np.mean(librosa.feature.mfcc(y=data,
                                             sr=sample_rate,
                                             n_mfcc=13))
        livedf2 = pd.DataFrame(data=mfccs).stack().to_frame().T
        twodim = np.expand_dims(livedf2, axis=2)
        return self.model.predict(twodim,
                                  batch_size=32,
                                  verbose=1)

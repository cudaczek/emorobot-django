import tensorflow as tf
import pandas as pd
import librosa
import numpy as np


class NeuralNetEvaluator:

    def __init__(self, file_name):
        self.file_name = file_name
        self.model = self.load_model()

    def load_model(self):
        return tf.keras.models.load_model(self.file_name)

    def predict(self, data, sample_rate):
        self.preprocess(data, sample_rate)
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

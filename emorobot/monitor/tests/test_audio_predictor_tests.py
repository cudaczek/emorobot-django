import struct
from unittest import TestCase

import librosa
from django.apps import apps

AUDIO_CLASSIFIER = apps.get_app_config('monitor').audio_classifier


def get_bytes(file_path):
    X, sample_rate = librosa.load(file_path, res_type='kaiser_fast', duration=1.0, sr=44100, offset=0.0)
    X = list(X)
    return struct.pack('>%sf' % len(X), *X)


class AudioRawDataPredictorTestCase(TestCase):
    def test_male_angry(self):
        bytes = get_bytes("monitor/tests/resources/1575747331male_angry.wav")
        prediction, labels = AUDIO_CLASSIFIER.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "male_angry")  #

    def test_male_happy(self):
        bytes = get_bytes("monitor/tests/resources/1575746637male_happy.wav")
        prediction, labels = AUDIO_CLASSIFIER.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "male_happy")  #

    def test_male_fearful(self):
        bytes = get_bytes("monitor/tests/resources/1575717697male_fearful.wav")
        prediction, labels = AUDIO_CLASSIFIER.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "male_fearful")

    def test_male_sad(self):
        bytes = get_bytes("monitor/tests/resources/1575715584male_sad.wav")
        prediction, labels = AUDIO_CLASSIFIER.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "male_sad")

    def test_female_calm(self):
        bytes = get_bytes("monitor/tests/resources/1575717749female_calm.wav")
        prediction, labels = AUDIO_CLASSIFIER.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "female_calm")

    def test_female_sad(self):
        bytes = get_bytes("monitor/tests/resources/1575715485female_sad.wav")
        prediction, labels = AUDIO_CLASSIFIER.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "female_sad")

    def test_female_fearful(self):
        bytes = get_bytes("monitor/tests/resources/1575715431female_fearful.wav")
        prediction, labels = AUDIO_CLASSIFIER.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "female_fearful")

    def test_female_angry(self):
        bytes = get_bytes("monitor/tests/resources/1575718318female_angry.wav")
        prediction, labels = AUDIO_CLASSIFIER.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "female_angry")

    def test_female_happy(self):
        bytes = get_bytes("monitor/tests/resources/1575746482female_happy.wav")
        prediction, labels = AUDIO_CLASSIFIER.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "female_happy")

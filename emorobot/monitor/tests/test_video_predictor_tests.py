from unittest import TestCase

from django.apps import apps

VIDEO_PREDICTOR = apps.get_app_config('monitor').video_predictor


def get_bytes(file_path):
    with open(file_path, "rb") as image:
        f = image.read()
        b = bytearray(f)
    return bytes(b)


class VideoRawDataPredictorTestCase(TestCase):
    def test_happiness(self):
        bytes = get_bytes("monitor/tests/resources/happy.jpg")
        prediction, labels = VIDEO_PREDICTOR.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "happy")

    def test_fear(self):
        bytes = get_bytes("monitor/tests/resources/fear.jpg")
        prediction, labels = VIDEO_PREDICTOR.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "fear")

    def test_anger(self):
        bytes = get_bytes("monitor/tests/resources/anger.jpg")
        prediction, labels = VIDEO_PREDICTOR.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "angry")

    def test_sadness(self):
        bytes = get_bytes("monitor/tests/resources/sad.jpg")
        prediction, labels = VIDEO_PREDICTOR.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "sad")

    def test_surprise(self):
        bytes = get_bytes("monitor/tests/resources/surprise.jpg")
        prediction, labels = VIDEO_PREDICTOR.predict(bytes)
        recognized_emotion = max(zip(prediction, labels), key=lambda x: x[0])[1]
        self.assertEqual(recognized_emotion, "surprise")

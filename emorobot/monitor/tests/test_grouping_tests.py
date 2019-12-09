from unittest import TestCase
from django.apps import apps

AUDIO_PREDICTOR = apps.get_app_config('monitor').audio_predictor
VIDEO_PREDICTOR = apps.get_app_config('monitor').video_predictor


# using own emotions groups
class VideoGroupTestCase(TestCase):
    def test_group_classical(self):
        predictions = [0.11, 0.44, 0.45]
        labels = ["sad", "happy", "angry"]
        values, category_names = VIDEO_PREDICTOR.group(predictions, labels)
        categories = {x[1]: x[0] for x in zip(values, category_names)}
        result = {"negative": 0.11 + 0.45, "positive": 0.44, "other": 0.0, "neutral": 0.0}
        self.assertDictEqual(categories, result)

    def test_group_no_existing_emotion(self):
        predictions = [0.11, 0.44, 0.45]
        labels = ["excited", "happy", "angry"]
        values, category_names = VIDEO_PREDICTOR.group(predictions, labels)
        categories = {x[1]: x[0] for x in zip(values, category_names)}
        result = {"negative": 0.45, "positive": 0.44, "other": 0.11, "neutral": 0.0}
        self.assertDictEqual(categories, result)

    def test_group_no_existing_emotion_in_own_dict_but_in_global(self):
        predictions = [0.11, 0.44, 0.45]
        labels = ["male_sad", "female_happy", "male_angry"]
        values, category_names = VIDEO_PREDICTOR.group(predictions, labels)
        categories = {x[1]: x[0] for x in zip(values, category_names)}
        result = {"negative": 0.0, "positive": 0.0, "other": 1.0, "neutral": 0.0}
        self.assertDictEqual(categories, result)


# using global emotional dictionary
class AudioGroupTestCase(TestCase):
    def test_group_classical(self):
        predictions = [0.11, 0.44, 0.45]
        labels = ["sad", "happy", "angry"]
        values, category_names = AUDIO_PREDICTOR.group(predictions, labels)
        categories = {x[1]: x[0] for x in zip(values, category_names)}
        result = {"negative": 0.45 + 0.11, "positive": 0.44, "other": 0.0, "neutral": 0.0}
        self.assertDictEqual(categories, result)

    def test_group_one_no_existing_emotion(self):
        predictions = [0.11, 0.44, 0.45]
        labels = ["excited", "male_happy", "female_angry"]
        values, category_names = AUDIO_PREDICTOR.group(predictions, labels)
        categories = {x[1]: x[0] for x in zip(values, category_names)}
        result = {"negative": 0.45, "positive": 0.44, "other": 0.11, "neutral": 0.0}
        self.assertDictEqual(categories, result)

    def test_group_all_no_existing_emotions_in_global_dict(self):
        predictions = [0.11, 0.44, 0.45]
        labels = ["excited", "scared", "tired"]
        values, category_names = AUDIO_PREDICTOR.group(predictions, labels)
        categories = {x[1]: x[0] for x in zip(values, category_names)}
        result = {"negative": 0.0, "positive": 0.0, "other": 1.0, "neutral": 0.0}
        self.assertDictEqual(categories, result)

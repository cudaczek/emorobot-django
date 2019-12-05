from unittest import TestCase

from django.apps import apps

VIDEO_PREDICTOR = apps.get_app_config('monitor').video_predictor


def get_bytes(file_path):
    with open(file_path, "rb") as image:
        f = image.read()
        b = bytearray(f)
    return bytes(b)

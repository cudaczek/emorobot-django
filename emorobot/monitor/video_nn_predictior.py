import json

import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model


class VideoRawDataPredictor:
    def __init__(self, filename):
        self.neural_net = VideoNeuralNetEvaluator(file_name=filename)

    def predict(self, raw_data):
        video_predictions = None
        video_labels = None
        if raw_data != b'':
            image_as_np = np.fromstring(raw_data, np.uint8)
            image = cv2.imdecode(image_as_np, cv2.IMREAD_COLOR)
            image = self.neural_net.preprocess(image)
            if image is None:
                video_predictions = [1.0]
                video_labels = ["no_face"]
                return video_predictions, video_labels
            video_predictions = self.neural_net.predict(image)
            video_labels = self.neural_net.names
        return video_predictions, video_labels

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


class VideoNeuralNetEvaluator:

    def __init__(self, file_name):
        self.graph = tf.get_default_graph()
        self.file_name = file_name
        self.names = []
        self.model = self.load_model()
        self.face_detection_model = self.load_face_detection_model()
        self.EMOTION_TARGET_SIZE = self.model.input_shape[1:3]

    def load_model(self):
        with open('resources/' + self.file_name + '_info.json') as json_file:
            model_infos = json.load(json_file)
            model_path = 'resources/' + model_infos["MODEL_FILE"]
            self.names = model_infos["EMOTIONS"]
            if "GROUPED_EMOTIONS" in model_infos.keys():
                self.grouped_emotions = model_infos["GROUPED_EMOTIONS"]
            else:
                self.grouped_emotions = self.load_global_emotions()
        model = load_model(model_path)
        return model

    def load_global_emotions(self):
        with open('resources/emotions_dict.json') as json_file:
            emotions = json.load(json_file)
        return emotions

    def load_face_detection_model(self):
        with open('resources/' + self.file_name + '_info.json') as json_file:
            model_infos = json.load(json_file)
            file_path = 'resources/' + model_infos["FACE_CLASSIFIER"]
        return cv2.CascadeClassifier(file_path)

    def predict(self, data):
        with self.graph.as_default():
            predictions = self.model.predict(data)[0]
        return predictions

    def preprocess(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # cv2.imwrite("Gray_Image.jpg", gray_image)
        faces = self.face_detection_model.detectMultiScale(gray_image)
        if len(faces) == 0:
            return None
        x1, x2, y1, y2 = self._apply_offsets(faces[0])
        gray_face = gray_image[y1:y2, x1:x2]
        # cv2.imwrite("gray_face.jpg", gray_face)
        try:
            gray_face = cv2.resize(gray_face, self.EMOTION_TARGET_SIZE)
        except:
            pass
        gray_face = self._preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        return gray_face

    def _apply_offsets(self, face_coordinates, ):
        x, y, width, height = face_coordinates
        return (x, x + width, y, y + height)

    def _preprocess_input(self, x, v2=True):
        x = x.astype('float32')
        x = x / 255.0
        if v2:
            x = x - 0.5
            x = x * 2.0
        return x

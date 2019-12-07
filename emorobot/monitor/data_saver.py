import io
import os
import struct
from datetime import datetime
from enum import Enum

import numpy as np
import pandas as pd
from PIL import Image
import soundfile as sf
from dataclasses import dataclass

from .predictors.predictor import Predictor


class DataType(Enum):
    EMOTIONS = 1
    EMOTIONS_FROM_RAW_DATA = 2
    EMOTIONS_GROUPED = 3
    EMOTIONS_FROM_RAW_DATA_GROUPED = 4


@dataclass
class EmotionData:
    file_name: str
    predictor: Predictor
    data_frame: pd.DataFrame = pd.DataFrame()
    grouped_data_frame: pd.DataFrame = pd.DataFrame()
    raw_data_data_frame: pd.DataFrame = pd.DataFrame()
    grouped_raw_data_data_frame: pd.DataFrame = pd.DataFrame()


class DataSaver:
    def __init__(self, video_nn, audio_nn):
        self.save_data = False
        self.directory_path = None
        self.video = EmotionData("video_emotion_data.csv", video_nn)
        self.audio = EmotionData("audio_emotion_data.csv", audio_nn)
        self.MAX_NUMBER_OF_ROW = 20

    def start_saving_data(self, directory_path):
        print("Start")
        self.save_data = True
        self.directory_path = directory_path

    def stop_saving_data(self):
        self.save_data = False

    def save_emotions(self, type, emotions, timestamp):
        if type == "video":
            data = self.video
        else:
            data = self.audio

        data.data_frame = data.data_frame.append(self.get_emotions_with_timestamp(emotions, timestamp),
                                                 ignore_index=True)
        data.grouped_data_frame = data.grouped_data_frame.append(
            self.get_grouped_emotions_with_timestamp(data.predictor, emotions, timestamp), ignore_index=True)
        if data.data_frame.shape[0] > self.MAX_NUMBER_OF_ROW:
            data.data_frame = data.data_frame.drop(data.data_frame.index[0])
        if data.grouped_data_frame.shape[0] > self.MAX_NUMBER_OF_ROW:
            data.grouped_data_frame = data.grouped_data_frame.drop(data.grouped_data_frame.index[0])
        if not self.save_data:
            return
        self.save_emotions_to_file(emotions, data)

    def get_emotions_with_timestamp(self, emotions_dict, timestamp):
        result = emotions_dict.copy()
        result.update({"timestamp": timestamp})
        return result

    def get_grouped_emotions_with_timestamp(self, predictor, emotions, timestamp):
        grouped_predictions, grouped_labels = predictor.group(list(emotions.values()), list(emotions.keys()))
        grouped_emotions = self.get_emotion_dictionary(grouped_labels, grouped_predictions)
        grouped_emotions["timestamp"] = timestamp
        return grouped_emotions

    def save_emotions_to_file(self, emotions, data):
        df = pd.DataFrame(emotions, index=[0])
        file_path = os.path.join(self.directory_path, data.file_name)
        with open(file_path, 'a') as f:
            df.to_csv(f, header=f.tell() == 0)

    def save_raw_data(self, type, bytes, timestamp):
        self.save_emotions_from_raw_data(type, bytes, timestamp)
        if not self.save_data:
            return
        if type == "video":
            self.save_picture(bytes)
        elif type == "audio":
            self.save_audio(bytes)

    def save_picture(self, bytes):
        image = Image.open(io.BytesIO(bytes))
        timestamp = datetime.timestamp(datetime.now())
        file_path = os.path.join(self.directory_path, str(int(timestamp)) + ".png")
        image.save(file_path, "PNG")

    def save_audio(self, bytes):
        if bytes != b'':
            count = int(len(bytes) / 4)
            floats = struct.unpack(">" + ('f' * count), bytes)
            timestamp = datetime.timestamp(datetime.now())
            file_path = os.path.join(self.directory_path, str(int(timestamp)) + ".wav")
            sf.write(file_path, np.array(floats), 44100, 'PCM_16', endian="FILE")

    def get_video_labels(self, type):
        return self.get_labels(self.video, type)

    def get_audio_labels(self, type):
        return self.get_labels(self.audio, type)

    def get_labels(self, data, type):
        if type == DataType.EMOTIONS:
            return self.get_labels_without_timestamp(data.data_frame)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA:
            return self.get_labels_without_timestamp(data.raw_data_data_frame)
        elif type == DataType.EMOTIONS_GROUPED:
            return self.get_labels_without_timestamp(data.grouped_data_frame)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA_GROUPED:
            return self.get_labels_without_timestamp(data.grouped_raw_data_data_frame)

    def get_labels_without_timestamp(self, data_frame):
        column_names = list(data_frame)
        if "timestamp" in column_names:
            column_names.remove("timestamp")
        return column_names

    def get_video_data(self, type):
        return self.get_data(type, self.video)

    def get_audio_data(self, type):
        return self.get_data(type, self.audio)

    def get_data(self, type, data):
        if type == DataType.EMOTIONS:
            return self.get_data_from_df(data.data_frame)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA:
            return self.get_data_from_df(data.raw_data_data_frame)
        elif type == DataType.EMOTIONS_GROUPED:
            return self.get_data_from_df(data.grouped_data_frame)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA_GROUPED:
            return self.get_data_from_df(data.grouped_raw_data_data_frame)

    def get_data_from_df(self, data_frame):
        data_list = []
        for index, row in data_frame.iterrows():
            x = row["timestamp"]
            time = datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')
            x = f"{time.year}-{time.month}-{time.day:02d} {time.hour:02d}:{time.minute:02d}:{time.second:02d}"
            biggest_val = 0
            y = None
            for key, value in row.items():
                if key == "timestamp":
                    continue
                if value > biggest_val:
                    biggest_val = value
                    y = key
            data_list.append({"x": x, "y": y})
        data_list.sort(key=lambda x: x["x"])
        return data_list

    def save_emotions_from_raw_data(self, type, bytes, timestamp):
        if type == "video":
            data = self.video
        else:
            data = self.audio
        emotions, grouped_emotions = self.predict_emotions(data.predictor, bytes, timestamp)
        data.raw_data_data_frame = data.raw_data_data_frame.append(emotions, ignore_index=True)
        if data.raw_data_data_frame.shape[0] > self.MAX_NUMBER_OF_ROW:
            data.raw_data_data_frame = data.raw_data_data_frame.drop(data.raw_data_data_frame.index[0])
        data.grouped_raw_data_data_frame = data.grouped_raw_data_data_frame.append(grouped_emotions, ignore_index=True)
        if data.grouped_raw_data_data_frame.shape[0] > self.MAX_NUMBER_OF_ROW:
            data.grouped_raw_data_data_frame = data.grouped_raw_data_data_frame.drop(
                data.grouped_raw_data_data_frame.index[0])

    def predict_emotions(self, predictor, bytes, timestamp):
        predictions, labels = predictor.predict(bytes)
        emotions = self.get_emotion_dictionary(labels, predictions)
        emotions["timestamp"] = timestamp
        grouped_predictions, grouped_labels = predictor.group(predictions, labels)
        grouped_emotions = self.get_emotion_dictionary(grouped_labels, grouped_predictions)
        grouped_emotions["timestamp"] = timestamp
        return emotions, grouped_emotions

    def get_emotion_dictionary(self, labels, predictions):
        result = {}
        for l, e in zip(labels, predictions):
            result[l] = e
        return result

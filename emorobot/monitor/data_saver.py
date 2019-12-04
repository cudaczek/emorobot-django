import io
import os
from datetime import datetime
from enum import Enum

import pandas as pd
from PIL import Image


class DataType(Enum):
    EMOTIONS = 1
    EMOTIONS_FROM_RAW_DATA = 2
    EMOTIONS_GROUPED = 3
    EMOTIONS_FROM_RAW_DATA_GROUPED = 4


class DataSaver:
    def __init__(self, video_nn, audio_nn):
        self.save_data = False
        self.directory_path = None
        self.VIDEO_FILE_NAME = "video_emotion_data.csv"
        self.AUDIO_FILE_NAME = "audio_emotion_data.csv"
        self.video_df = pd.DataFrame()
        self.audio_df = pd.DataFrame()
        self.video_grouped_df = pd.DataFrame()
        self.audio_grouped_df = pd.DataFrame()
        self.video_nn = video_nn
        self.audio_nn = audio_nn
        self.video_raw_data_df = pd.DataFrame()
        self.audio_raw_data_df = pd.DataFrame()
        self.video_grouped_raw_data_df = pd.DataFrame()
        self.audio_grouped_raw_data_df = pd.DataFrame()
        self.MAX_NUMBER_OF_ROW = 20

    def start_saving_data(self, directory_path):
        print("Start")
        self.save_data = True
        self.directory_path = directory_path

    def stop_saving_data(self):
        self.save_data = False

    def save_emotions(self, type, emotions, timestamp):
        if type == "video":
            self.save_video_emotions(emotions, timestamp)
        elif type == "audio":
            self.save_audio_emotions(emotions, timestamp)

    def save_video_emotions(self, emotions, timestamp):
        self.video_df = self.video_df.append(self.get_emotions_with_timestamp(emotions, timestamp), ignore_index=True)
        self.video_grouped_df = self.video_grouped_df.append(
            self.get_grouped_emotions_with_timestamp(self.video_nn, emotions, timestamp), ignore_index=True)
        if self.video_df.shape[0] > self.MAX_NUMBER_OF_ROW:
            self.video_df = self.video_df.drop(self.video_df.index[0])
        if self.video_grouped_raw_data_df.shape[0] > self.MAX_NUMBER_OF_ROW:
            self.video_grouped_raw_data_df = self.video_grouped_raw_data_df.drop(
                self.video_grouped_raw_data_df.index[0])
        if not self.save_data:
            return
        self.save_emotions_to_file(emotions, "video")

    def save_audio_emotions(self, emotions, timestamp):
        self.audio_df = self.audio_df.append(self.get_emotions_with_timestamp(emotions, timestamp), ignore_index=True)
        self.audio_grouped_df = self.audio_grouped_df.append(
            self.get_grouped_emotions_with_timestamp(self.audio_nn, emotions, timestamp), ignore_index=True)
        if self.audio_df.shape[0] > self.MAX_NUMBER_OF_ROW:
            self.audio_df = self.audio_df.drop(self.audio_df.index[0])
        if self.audio_grouped_df.shape[0] > self.MAX_NUMBER_OF_ROW:
            self.audio_grouped_df = self.audio_grouped_df.drop(self.audio_grouped_df.index[0])
        if not self.save_data:
            return
        self.save_emotions_to_file(emotions, "audio")

    def get_emotions_with_timestamp(self, emotions_dict, timestamp):
        result = emotions_dict.copy()
        result.update({"timestamp": timestamp})
        return result

    def get_grouped_emotions_with_timestamp(self, predictor, emotions, timestamp):
        grouped_predictions, grouped_labels = predictor.group(list(emotions.values()), list(emotions.keys()))
        grouped_emotions = self.get_emotion_dictionary(grouped_labels, grouped_predictions)
        grouped_emotions["timestamp"] = timestamp
        return grouped_emotions

    def save_emotions_to_file(self, emotions, type):
        df = pd.DataFrame(emotions, index=[0])
        file_path = os.path.join(self.directory_path, self.AUDIO_FILE_NAME if type == "audio" else self.VIDEO_FILE_NAME)
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
        # TODO
        pass

    def get_video_labels(self, type):
        if type == DataType.EMOTIONS:
            return self.get_labels(self.video_df)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA:
            return self.get_labels(self.video_raw_data_df)
        elif type == DataType.EMOTIONS_GROUPED:
            return self.get_labels(self.video_grouped_df)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA_GROUPED:
            return self.get_labels(self.video_grouped_raw_data_df)

    def get_audio_labels(self, type):
        if type == DataType.EMOTIONS:
            return self.get_labels(self.audio_df)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA:
            return self.get_labels(self.audio_raw_data_df)
        elif type == DataType.EMOTIONS_GROUPED:
            return self.get_labels(self.audio_grouped_df)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA_GROUPED:
            return self.get_labels(self.audio_grouped_raw_data_df)

    def get_labels(self, data_frame):
        column_names = list(data_frame)
        if "timestamp" in column_names:
            column_names.remove("timestamp")
        return column_names

    def get_video_data(self, type):
        if type == DataType.EMOTIONS:
            return self.get_data_from_df(self.video_df)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA:
            return self.get_data_from_df(self.video_raw_data_df)
        elif type == DataType.EMOTIONS_GROUPED:
            return self.get_data_from_df(self.video_grouped_df)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA_GROUPED:
            return self.get_data_from_df(self.video_grouped_raw_data_df)

    def get_audio_data(self, type):
        if type == DataType.EMOTIONS:
            return self.get_data_from_df(self.audio_df)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA:
            return self.get_data_from_df(self.audio_raw_data_df)
        elif type == DataType.EMOTIONS_GROUPED:
            return self.get_data_from_df(self.audio_grouped_df)
        elif type == DataType.EMOTIONS_FROM_RAW_DATA_GROUPED:
            return self.get_data_from_df(self.audio_grouped_raw_data_df)

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
            emotions, grouped_emotions = self.predict_emotions(self.video_nn, bytes, timestamp)
            self.video_raw_data_df = self.video_raw_data_df.append(emotions, ignore_index=True)
            if self.video_raw_data_df.shape[0] > self.MAX_NUMBER_OF_ROW:
                self.video_raw_data_df = self.video_raw_data_df.drop(self.video_df.index[0])
            self.video_grouped_raw_data_df = self.video_grouped_raw_data_df.append(grouped_emotions, ignore_index=True)
            if self.video_grouped_raw_data_df.shape[0] > self.MAX_NUMBER_OF_ROW:
                self.video_grouped_raw_data_df = self.video_grouped_raw_data_df.drop(self.video_df.index[0])
        elif type == "audio":
            emotions, grouped_emotions = self.predict_emotions(self.audio_nn, bytes, timestamp)
            self.audio_raw_data_df = self.audio_raw_data_df.append(emotions, ignore_index=True)
            if self.audio_raw_data_df.shape[0] > self.MAX_NUMBER_OF_ROW:
                self.audio_raw_data_df = self.audio_raw_data_df.drop(self.audio_raw_data_df.index[0])
            self.audio_grouped_raw_data_df = self.audio_grouped_raw_data_df.append(grouped_emotions, ignore_index=True)
            if self.audio_grouped_raw_data_df.shape[0] > self.MAX_NUMBER_OF_ROW:
                self.audio_grouped_raw_data_df = self.audio_grouped_raw_data_df.drop(
                    self.audio_grouped_raw_data_df.index[0])

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

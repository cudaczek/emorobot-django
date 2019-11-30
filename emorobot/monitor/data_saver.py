import io
import os
from datetime import datetime

import pandas as pd
from PIL import Image


class DataSaver:
    def __init__(self):
        self.save_data = False
        self.directory_path = None
        self.VIDEO_FILE_NAME = "video_emotion_data.csv"
        self.AUDIO_FILE_NAME = "audio_emotion_data.csv"
        self.video_df = pd.DataFrame()
        self.audio_df = pd.DataFrame()
        self.MAX_NUMBER_OF_ROW = 300

    def start_saving_data(self, directory_path):
        print("Start")
        self.save_data = True
        self.directory_path = directory_path

    def stop_saving_data(self):
        self.save_data = False

    def save_emotions(self, name, emotions, timestamp):
        if name == "video":
            self.save_video_emotions(emotions, timestamp)
        else:
            self.save_audio_emotions(emotions, timestamp)

    def save_video_emotions(self, emotions, timestamp):
        emotions.update({"timestamp": timestamp})
        self.video_df = self.video_df.append(emotions, ignore_index=True)
        if self.video_df.shape[0] > self.MAX_NUMBER_OF_ROW:
            self.video_df = self.video_df.drop(self.video_df.index[0])
        if not self.save_data:
            return
        self.save_emotions_to_file(emotions, "video")

    def save_audio_emotions(self, emotions, timestamp):
        emotions.update({"timestamp": timestamp})
        self.audio_df = self.audio_df.append(emotions, ignore_index=True)
        if self.audio_df.shape[0] > self.MAX_NUMBER_OF_ROW:
            self.audio_df = self.audio_df.drop(self.audio_df.index[0])
        if not self.save_data:
            return
        self.save_emotions_to_file(emotions, "audio")

    def save_emotions_to_file(self, emotions, name):
        df = pd.DataFrame(emotions, index=[0])
        file_path = os.path.join(self.directory_path, self.AUDIO_FILE_NAME if name == "audio" else self.VIDEO_FILE_NAME)
        with open(file_path, 'a') as f:
            df.to_csv(f, header=f.tell() == 0)

    def save_raw_data(self, name, bytes, timestamp):
        if not self.save_data:
            return
        if name == "video":
            self.save_picture(bytes)
        else:
            self.save_audio(bytes)

    def save_picture(self, bytes):
        image = Image.open(io.BytesIO(bytes))
        timestamp = datetime.timestamp(datetime.now())
        file_path = os.path.join(self.directory_path, str(int(timestamp)) + ".png")
        image.save(file_path, "PNG")

    def save_audio(self, bytes):
        # TODO
        pass

    def get_video_labels(self):
        column_names = list(self.video_df.columns.values)
        column_names.remove("timestamp")
        return column_names

    def get_audio_labels(self):
        column_names = list(self.audio_df.columns.values)
        column_names.remove("timestamp")
        return column_names

    def get_video_data(self):
        return self.get_data_from_df(self.video_df)

    def get_audio_data(self):
        return self.get_data_from_df(self.audio_df)

    def get_data_from_df(self, data_frame):
        data_list = []
        for index, row in data_frame.iterrows():
            x = row["timestamp"]

            time = datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')
            x = f"{time.year}-{time.month}-{time.day}T{time.hour}:{time.minute}:{time.second}+01:00"
            biggest_val = 0
            y = None
            for key, value in row.items():
                if key == "timestamp":
                    continue
                if value > biggest_val:
                    biggest_val = value
                    y = key
            data_list.append({"x": x, "y": y})
        return data_list

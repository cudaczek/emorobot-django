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
        if not self.save_data:
            return
        self.save_emotions_to_file(emotions, "video")

    def save_audio_emotions(self, emotions, timestamp):
        emotions.update({"timestamp": timestamp})
        self.audio_df = self.audio_df.append(emotions, ignore_index=True)
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
        file_path = os.path.join(self.directory_path, str(int(timestamp)))
        image.save(file_path, "PNG")

    def save_audio(self, bytes):
        # TODO
        pass

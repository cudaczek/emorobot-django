import io
import os
from datetime import datetime

import numpy
import pandas as pd
import scipy.io.wavfile
from PIL import Image


class DataSaver:
    def __init__(self):
        self.save_data = False
        self.directory_path = None
        self.video_df = []
        self.json_audio = []
        self.json_video_iterator = 1
        self.json_audio_iterator = 1
        self.VIDEO_FILE_NAME = "video_emotion_data.csv"
        self.AUDIO_FILE_NAME = "audio_emotion_data.csv"

    def start_saving_data(self, directory_path):
        print("Start")
        self.save_data = True
        self.directory_path = directory_path

    def stop_saving_data(self):
        self.save_data = False

    def save_emotions(self, name, emotions):
        if not self.save_data:
            return
        df = pd.DataFrame(emotions, index=[0])
        if name == "video":
            file_path = os.path.join(self.directory_path, self.VIDEO_FILE_NAME)
            with open(file_path, 'a') as f:
                df.to_csv(f, header=f.tell() == 0)
        elif name == "audio":
            file_path = os.path.join(self.directory_path, self.AUDIO_FILE_NAME)
            print(file_path)
            with open(file_path, 'a') as f:
                df.to_csv(f, header=f.tell() == 0)

    def save_raw_data(self, name, bytes):
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
        timestamp = datetime.timestamp(datetime.now())
        file_path = os.path.join(self.directory_path, str(int(timestamp)))
        # with open(file_path + '.wav', mode='bx') as f:
        #     f.write(bytes)
        print("saving")
        b = numpy.array(bytes, dtype=numpy.int16)
        scipy.io.wavfile.write(f"./blabla.wav",
                               16000, b)

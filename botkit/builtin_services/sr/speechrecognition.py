import os
import subprocess

import ffmpy
import speech_recognition as sr


class VoiceRecognitionClient:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    @staticmethod
    def convert_audio_ffmpeg(in_file, out_file):
        if os.path.exists(out_file):
            os.remove(out_file)
        ff = ffmpy.FFmpeg(inputs={in_file: None}, outputs={out_file: None})
        ff.run(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_file

    def recognize(self, filepath, language=None):
        with sr.AudioFile(filepath) as source:
            audio = self.recognizer.record(source)  # read the entire audio file
        return self.recognizer.recognize_google_cloud(audio, None, language=language)

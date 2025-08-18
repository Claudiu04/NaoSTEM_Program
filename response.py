# -*- coding: utf-8 -*-
from __future__ import print_function
from naoqi import ALProxy
import requests
import time

IP = "127.0.0.1"
SERVER_URL = "http://192.168.100.163:5000/transcribe" 

def replace_diacritics(text):
    replacements = {
        u"ă": u"a", u"â": u"a", u"î": u"i",
        u"ș": u"s", u"ş": u"s", u"ț": u"t", u"ţ": u"t",
        u"Ă": u"A", u"Â": u"A", u"Î": u"I",
        u"Ș": u"S", u"Ş": u"S", u"Ț": u"T", u"Ţ": u"T"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def record_and_send():
    try:
        audio_recorder = ALProxy("ALAudioRecorder", IP, 9559)
        file_path = "/home/nao/record.wav"
        audio_recorder.startMicrophonesRecording(file_path, "wav", 16000, (1, 0, 0, 0))
        print("Recording for 5 seconds...")
        time.sleep(5)
        audio_recorder.stopMicrophonesRecording()
        print("Recording stopped, saved to " + file_path)

        with open(file_path, "rb") as f:
            files = {"audio": f}
            response = requests.post(SERVER_URL, files=files)

        if response.status_code == 200:
            data = response.json()
            transcription = data.get("transcription", "")
            reply_text = data.get("reply", "")
            print("Transcription: " + transcription.encode("utf-8"))
            print("Reply: " + reply_text.encode("utf-8"))


            clean_reply = replace_diacritics(reply_text)

            player = ALProxy("ALAudioPlayer", IP, 9559)
            player.playFile("/home/nao/response.mp3")

        else:
            print("Server error:", response.status_code, response.text)

    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    record_and_send()

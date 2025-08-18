from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
from gtts import gTTS
import tempfile
import os
import paramiko

app = Flask(__name__)

# Încarcă modelul Whisper
model = WhisperModel("medium", device="cpu", compute_type="int8")

# NAO settings
NAO_IP = "192.168.100.107"
NAO_USER = "nao"
NAO_PASS = "nao"
NAO_AUDIO_PATH = "/home/nao/response.mp3"  # acum folosim direct MP3

def generate_response(text):
    text = text.lower()
    if "ce faci" in text:
        return """Dormeau adânc sicriele de plumb,
                Şi flori de plumb şi funerar vestmint --
                Stam singur în cavou... si era vint...
                Si scirtiiau coroanele de plumb.

                Dormea întors amorul meu de plumb
                Pe flori de plumb, si-am inceput să-l strig --
                Stam singur lângă mort... si era frig...
                Si-i atirnau aripile de plumb."""
    elif "cum te numesti" in text:
        return "Mă numesc Nao, robotul tău personal."
    else:
        return "Îmi pare rău, nu am înțeles întrebarea."

def generate_mp3_from_text(text, mp3_path):
    tts = gTTS(text, lang="ro")
    tts.save(mp3_path)

def send_to_nao(local_path, remote_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NAO_IP, username=NAO_USER, password=NAO_PASS)
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_file.save(tmp.name)
        segments, info = model.transcribe(tmp.name, language="ro")
        transcription = "".join([segment.text for segment in segments])

    print("Transcris:", transcription)

    reply = generate_response(transcription)
    print("Răspuns generat:", reply)

    generate_mp3_from_text(reply, "response.mp3")

    send_to_nao("response.mp3", NAO_AUDIO_PATH)

    return jsonify({"transcription": transcription, "reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, render_template, request, jsonify, send_from_directory
import asyncio
import edge_tts  # Make sure this is installed via pip
import sounddevice as sd
import wavio
import numpy as np
import os
import threading

app = Flask(__name__)

# Ensure the output directory exists
if not os.path.exists('static/output'):
    os.makedirs('static/output')

# Variables for TTS
VOICES = [
    'en-US-GuyNeural', 'en-US-JennyNeural',
    'en-AU-NatashaNeural', 'en-AU-WilliamNeural',
    'en-CA-ClaraNeural', 'en-CA-LiamNeural',
    'en-GB-LibbyNeural','YOUR RECORDED VOICE'
]

# Variables for recording
FS = 44100  # Sample rate
recording = False
audio = []

# TTS Function
async def tts(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print(f"TTS audio saved as {output_file}")

# Recording Functions
def callback(indata, frames, time, status):
    if recording:
        audio.append(indata.copy())

def start_recording():
    global recording, audio
    recording = True
    audio = []
    with sd.InputStream(samplerate=FS, channels=2, dtype=np.int16, callback=callback):
        while recording:
            sd.sleep(1000)

def stop_recording():
    global recording
    recording = False
    print("Recording stopped.")

def save_recording(output_file):
    if audio:
        audio_data = np.concatenate(audio, axis=0)
        wavio.write(output_file, audio_data, FS, sampwidth=2)
        print(f"Audio saved as {output_file}")
    else:
        print("No audio data to save.")

@app.route('/')
def index():
    return render_template('index.html', voices=VOICES)

@app.route('/tts', methods=['POST'])
def tts_route():
    text = request.form['text']
    voice = request.form['voice']
    output_file = request.form.get('output_file', 'output.mp3')
    output_path = f'static/output/{output_file}'
    
    # Run the TTS task in the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(tts(text, voice, output_path))
    
    return jsonify({"message": f"TTS audio saved as {output_path}", "file_url": output_path})

@app.route('/record/start', methods=['POST'])
def start_recording_route():
    global recording
    if not recording:
        threading.Thread(target=start_recording).start()
    return jsonify({"message": "Recording started"})

@app.route('/record/stop', methods=['POST'])
def stop_recording_route():
    global recording
    recording = False
    output_file = request.form.get('output_file', 'mic_input.wav')
    output_path = f'static/output/{output_file}'
    save_recording(output_path)
    return jsonify({"message": f"Recording stopped and saved as {output_path}", "file_url": output_path})

@app.route('/recorded_files')
def recorded_files():
    recorded_files_path = 'static/output'
    files = os.listdir(recorded_files_path)
    files = [file for file in files if file.endswith('.wav')]  # Filter for only .wav files
    return render_template('recorded_files.html', files=files)

@app.route('/static/output/<filename>')
def download_file(filename):
    return send_from_directory('static/output', filename)

if __name__ == '__main__':
    app.run(debug=True)

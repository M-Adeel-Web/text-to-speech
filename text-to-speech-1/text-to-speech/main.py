#code for main.py :
import asyncio
import edge_tts
import sounddevice as sd
import wavio
import numpy as np

# Variables for TTS
VOICES = [
    'YOUR RECORDED VOICE', 'US-JennyNeural',
    'NatashaNeural', 'AU-WilliamNeural',
    'ClaraNeural', 'CA-LiamNeural',
    'LibbyNeural'
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
        print("Recording... Press Enter to stop.")
        input()
        stop_recording()

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

# Main function
async def main():
    choice = input("Do you want to convert text to speech or record audio from the microphone? (tts/record): ").strip().lower()
    
    if choice == 'tts':
        text = input("Enter the text you want to convert to speech: ").strip()
        
        print("Available voices:")
        for i, voice in enumerate(VOICES):
            print(f"{i + 1}. {voice}")
        
        voice_choice = int(input("Enter the number corresponding to your desired voice: ").strip()) - 1
        voice = VOICES[voice_choice]
        
        default_file = "output.mp3"
        output_file = input(f"Enter the output file name (default: {default_file}): ").strip()
        if not output_file:
            output_file = default_file
        
        await tts(text, voice, output_file)
    
    elif choice == 'record':
        default_file = "mic_input.wav"
        output_file = input(f"Enter the output file name (default: {default_file}): ").strip()
        if not output_file:
            output_file = default_file

        start_recording()
        save_recording(output_file)
    
    else:
        print("Invalid choice. Please enter 'tts' or 'record'.")

# Run the event loop
loop = asyncio.get_event_loop_policy().get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()
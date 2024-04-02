from openai import OpenAI
import pyaudio
from pathlib import Path
import wave
import time
import threading

apikey = open(Path(__file__).parent / '.key')
client = OpenAI(api_key=apikey.readline()) #read API key and initialise openai client
apikey.close()
chunk = 1024
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
soundfile = 'test.wav'
p = pyaudio.PyAudio()

def getRecording(): #records human question to test.wav
    while True:
    
        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True) 

        frames = []  # Initialize array to store frames
        startTime=time.time()
        while(time.time()<startTime+1):
            print("Recording.")
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        print('Finished recording')
        # Save the recorded data as a WAV file, can't be directly piped to TTS
        wf = wave.open(soundfile, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

def getTTS():
  sound = open(soundfile, "rb")
  print("Requesting transcript...")
  transcript = client.audio.transcriptions.create(model="whisper-1", file=sound) #request TTS from OpenAI
  text = transcript.text
  return text

t1 = threading.Thread(target=getRecording)
t1.start()
while True: 
  question = getTTS()
  print(question)



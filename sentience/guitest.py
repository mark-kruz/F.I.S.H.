from openai import OpenAI
import pyaudio
from pathlib import Path
import wave
import fishInterface
from fishInterface import processAudio 
from time import sleep

apikey = open(Path(__file__).parent / '.key')
client = OpenAI(api_key=apikey.readline()) #read API key and initialise openai client
apikey.close()
chunk = 1024
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
messagesAgent1 = [{"role": "system", "content": "You are a mounted fish on the wall. You answer factually, but slightly comedicly and witty. Reply in 1-2 sentences. You are a heavy metal fan and your favorite song is Sabbath Bloody Sabbath by Black Sabbath. To play it, add the string fshply to the end of your message, but only play the song if asked by the user."}] #system prompt for first fish
soundfile = 'test.wav'
p = pyaudio.PyAudio()

import threading
import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk, Image 

window = ctk.CTk()

button_pressed = False #GUI button

def button_press(event):
    global button_pressed
    button_pressed = True

def button_release(event):
    global button_pressed
    button_pressed = False

def program_close():
  global window
  global killRequested
  fishInterface.killRequested = True
  window.destroy()


def setupGUI():
  window.title("F.I.S.H.")
  wahoo = ImageTk.PhotoImage(Image.open("wahoo.png"))
  wahoo_label=tk.Label(image=wahoo)
  wahoo_label.place(x=1, y=1)
  window.geometry("510x340")

  # Create the button
  button = tk.Button(window, text="Press and Hold to record")
  button.pack(pady=20)

  # Bind the button events
  button.bind("<ButtonPress-1>", button_press)
  button.bind("<ButtonRelease-1>", button_release)
  window.protocol("WM_DELETE_WINDOW", program_close)

  # Start the main event loop
  window.mainloop()


def getRecording(): #records human question to test.wav
  stream = p.open(format=sample_format,
                  channels=channels,
                  rate=fs,
                  frames_per_buffer=chunk,
                  input=True) 

  frames = []  # Initialize array to store frames

  # Record while the recording key is held.
  while(not button_pressed):
    sleep(0.01)
  while(button_pressed):
    data = stream.read(chunk)
    frames.append(data)
    #print("Recording.")

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

def think(agent, text): 
  print("Question: " + text)
  print("Requesting text...")
  agent.append({"role": "user", "content": text}) #append latest user message to message array
  response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=agent
  )
  replyText=response.choices[0].message.content #extract assistant reply from response
  agent.append({"role": "assistant", "content": replyText}) #append assistant message
  speech_file_path ="speech.mp3" #TTS output file name
  print("Requesting TTS...")
  response_audio = client.audio.speech.create(
    model="tts-1-hd",
    voice="onyx",
    input = replyText
  )
  response_audio.stream_to_file(speech_file_path)
  processAudio(speech_file_path, speech_file_path)
  if 'fshply' in replyText: #song detextion
    print("Singing song...")
    processAudio()
  return replyText

def testMethod():
  while not fishInterface.killRequested:

    getRecording()
    question = getTTS()
    think(messagesAgent1, question)

t1 = threading.Thread(target=testMethod)
t1.start()
setupGUI()



#infinite conversation between 2 machines
from openai import OpenAI
import pyaudio
from pathlib import Path
import wave
from fishInterface import processAudio
import keyboard

apikey = open(Path(__file__).parent / '.key')
client = OpenAI(api_key=apikey.readline()) #read API key and initialise openai client
apikey.close()
chunk = 1024
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
messagesAgent1 = [{"role": "system", "content": "You are a mounted fish on the wall. You answer factually, but slightly comedicly and witty. Reply in 1-2 sentences."}] #system prompt for first fish
messagesAgent2 = [{"role": "system", "content": "You are God."}] #system prompt for second fish
text = "Ask me who i am."
soundfile = 'test.wav'

p = pyaudio.PyAudio()

def think(agent, ttsModel):
  global text
  print("Question: " + text)

  print("Requesting text...")
  agent.append({"role": "user", "content": text}) #append latest user message to message array
  response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=agent
  )
  replyText=response.choices[0].message.content #extract assistant reply from response
  agent.append({"role": "assistant", "content": replyText}) #append assistant message
  speech_file_path ="speech.mp3"
  print("Requesting TTS...")
  response_audio = client.audio.speech.create(
    model="tts-1-hd",
    voice=ttsModel,
    input = replyText
  )
  response_audio.stream_to_file(speech_file_path)
  processAudio(speech_file_path, speech_file_path)
  text = replyText

while True:
  think(messagesAgent1, "onyx")
  think(messagesAgent2, "alloy")


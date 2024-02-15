import numpy as np
import pygame
import librosa
from pySerialTransfer import pySerialTransfer as txfer
from time import sleep
from collections import deque

class struct(object):
    mouthPosition = 0
    bodyState = 0
    eyeState = 0
    tailState = 0

# Constants
SERVO_MAX = 2000
POWER_AT_MOUTH_FULLY_OPEN = 0.16
AUDIO_SHORT_CODE = 'sbs'
default_AUDIO_PATH_ANALYSIS = 'C:/Users/xbox3/Documents/PlatformIO/Projects/singing_z-800/backend/vocals_'+AUDIO_SHORT_CODE+'.wav'
default_AUDIO_PATH_PLAYBACK = 'C:/Users/xbox3/Documents/PlatformIO/Projects/singing_z-800/backend/'+AUDIO_SHORT_CODE+'.flac'
default_AUDIO_PATH_DRUMS = 'C:/Users/xbox3/Documents/PlatformIO/Projects/singing_z-800/backend/drums_'+AUDIO_SHORT_CODE+'.wav'
TIME_PER_STEP = 0.02  # seconds
SMOOTHING_WINDOW_SIZE = 5  # Adjust this value based on your needs

servo_positions = deque(maxlen=SMOOTHING_WINDOW_SIZE)


def map_average_to_microseconds(average_power):
    """Map average power to servo microseconds."""
    us = (1000 * average_power / POWER_AT_MOUTH_FULLY_OPEN) + 1000
    us = max(1000, min(us, SERVO_MAX))
    
    if us < 1100:
        us = 1000  # Decrease servo chatter at low amplitudes
    return us

def compute_rms(samples):
    """Compute the RMS of the provided samples."""
    return np.sqrt(np.mean(samples**2))

def processAudio(AUDIO_PATH_PLAYBACK = default_AUDIO_PATH_PLAYBACK, AUDIO_PATH_ANALYSIS = default_AUDIO_PATH_ANALYSIS, AUDIO_PATH_DRUMS = default_AUDIO_PATH_DRUMS):
    #connect to Arduino
    try:
        testStruct = struct
        link = txfer.SerialTransfer('COM5')
        link.open()
        link_state=True
        sleep(2)
    except:
        #link.close()
        link_state=False
        print("Arduino connection failed!")

    pygame.mixer.init()
    pygame.mixer.music.load(AUDIO_PATH_PLAYBACK)

    y, sr = librosa.load(AUDIO_PATH_ANALYSIS)
    samples_per_step = sr * TIME_PER_STEP
    samples0 = 0
    samples1 = samples_per_step

    # Load and analyze the drum track for beat detection
    y_drums, sr_drums = librosa.load(AUDIO_PATH_DRUMS)
    onset_env = librosa.onset.onset_strength(y=y_drums, sr=sr_drums)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr_drums)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr_drums)

    pygame.mixer.music.play()
    start_time = pygame.mixer.music.get_pos()
    beat_counter=0
    lastBeatTime=0
    predictedNextBeat=0
    pseudoBeatNotComplete=False
    while samples1 < len(y):
        if pygame.mixer.music.get_pos() - start_time >= TIME_PER_STEP * 1000:
            subset = y[int(samples0):int(samples1)]
            rms = compute_rms(subset)
            servo_position = map_average_to_microseconds(rms)

            # Add the new position to the deque and get the average
            servo_positions.append(servo_position)
            smoothed_position = sum(servo_positions) // len(servo_positions)
            testStruct.mouthPosition = smoothed_position
            if link_state == True: #send data only if good connection to arduino
                warning = "" #clear warning flag
                sendSize = 0
                sendSize = link.tx_obj(int(testStruct.mouthPosition), start_pos=sendSize)
                sendSize = link.tx_obj(testStruct.bodyState, start_pos=sendSize)
                sendSize = link.tx_obj(testStruct.eyeState, start_pos=sendSize)
                sendSize = link.tx_obj(testStruct.tailState, start_pos=sendSize)
                link.send(sendSize)
            else: warning = "Bad serial connection!"
            print(pygame.mixer.music.get_pos(), smoothed_position, testStruct.tailState, warning)
            current_time_seconds = pygame.mixer.music.get_pos() / 1000.0 #current position in the playback audio

            #try to double time the tail
            if ((lastBeatTime+(predictedNextBeat/2) <= current_time_seconds) & pseudoBeatNotComplete):
                testStruct.tailState = 1-testStruct.tailState    
                pseudoBeatNotComplete=False
            # Check for a beat close to the current time
            if any(abs(current_time_seconds - beat_time) < TIME_PER_STEP for beat_time in beat_times):
                beat_counter += 1
                if beat_counter == 2:
                    predictedNextBeat = current_time_seconds-lastBeatTime
                    testStruct.tailState = 1-testStruct.tailState 
                    pseudoBeatNotComplete=True
                    lastBeatTime=current_time_seconds
                    beat_counter=0
            
            samples0 += samples_per_step
            samples1 += samples_per_step
            start_time += TIME_PER_STEP * 1000

if __name__ == '__main__':
    processAudio()

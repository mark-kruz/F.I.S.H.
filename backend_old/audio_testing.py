import numpy as np
import time
import librosa
from IPython.display import Audio
from IPython.display import display
import subprocess
import pygame

def mapAverageToMicroseconds(averagePower): #0 - 0.2 on the input maps to 1000-2000 on the output
    servoMax=2000
    powerAtMouthFullyOpen=0.2
    us = (1000*averagePower/powerAtMouthFullyOpen) + 1000 # map to the approximate servo range
    if us>servoMax:
        us=servoMax #limit to servo max position
    if us<1100:
        us=1000 #try to decrease servo chatter at low amplitudes
    return us

def Main():
    pygame.mixer.init()
    audio = 'C:/Users/xbox3/Documents/PlatformIO/Projects/singing_z-800/backend/vocals.wav'
    pygame.mixer.music.load(audio)
    y, sr = librosa.load(audio)
    absolute_amplitudes = np.absolute(y)
    time_per_step = 0.1 #in seconds
    samplesPerStep = sr*time_per_step

    soundPosition=0
    samples0=0
    samples1=samplesPerStep #the window between which to average the value
    pygame.mixer.music.play()
    startTime = pygame.mixer.music.get_pos() #some sort of synchronization for time is needed
    
    while samples1<absolute_amplitudes.size:
        if pygame.mixer.music.get_pos()>=(startTime+(time_per_step*1000)):
            startTime=round((pygame.mixer.music.get_pos()/100))*100 #workaround hack to mitigate drifting time from the delay of the if clause to the start time being registered
            subset = absolute_amplitudes[int(samples0):int(samples1)] #extract one timestep from the array for averaging
            average = np.mean(subset)
            sevoPos = mapAverageToMicroseconds(average)
            print(pygame.mixer.music.get_pos())
            print(sevoPos)
            print()
            soundPosition += time_per_step
            samples0 += samplesPerStep
            samples1 += samplesPerStep
            #if soundPosition > 20:
        #     break
Main()
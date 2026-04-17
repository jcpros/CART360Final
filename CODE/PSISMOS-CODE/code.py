###SOUND GENERATOR CODE ###
### Some lines in the main loop (reverb) have been intentionally left commented. The reverb output sounded interesting and worth exploring, but was more unstable/randomly noisy (perhaps hard to compute real-time reverb)
### Some of the code here was developed using classes (Wavetable) and functions written by Tod Kurt/todbot https://github.com/todbot/CircuitPython_Synthio_Tutorial. Huge thanks to him!
import time
import board
import adafruit_mpu6050
import busio # contains the interface for i2c
import synthio
import audiobusio
import audiomixer
import digitalio 
import ulab.numpy as np
import adafruit_mprls
import audiofilters
import audiodelays
import audiofreeverb
from wavetable import Wavetable


##Create audio out
audio = audiobusio.I2SOut(bit_clock=board.GP10, word_select=board.GP11, data=board.GP12)

##Create synthesizer objects
kickSynth = synthio.Synthesizer(sample_rate=44100)
kickSynth.envelope = synthio.Envelope(attack_time=0, decay_time = 0.3, sustain_level=1, release_time = 0.3)
droneSynth = synthio.Synthesizer(sample_rate=44100)
droneSynth.envelope = synthio.Envelope(attack_time=0.1, decay_time=0.5, release_time=0.5, attack_level=1)

##Create mixer object
mixer = audiomixer.Mixer(sample_rate = 44100, buffer_size = 1024, channel_count=2)



#Import and create wavetable
wavetable_fname = "wavetables/MICROBRU.WAV"  # from http://waveeditonline.com/
wavetable1 = Wavetable(wavetable_fname)
wavetable_fname2 = "wavetables/NOMAD.WAV"
wavetable2 = Wavetable(wavetable_fname2)

#Create Notes
kickNote = synthio.Note(frequency=40, waveform=wavetable1.waveform, amplitude = 0.9)
droneNote = synthio.Note(frequency=50, waveform=wavetable2.waveform, amplitude = 0.6)



# create a positive ramp-up-down LFO to scan through the waveetable
wave_lfo = synthio.LFO(rate=0.05, waveform=np.array((0,32767), dtype=np.int16))
tremolo = synthio.LFO(rate=5, scale=0.5, offset=0.5)
tremolo_mod = synthio.LFO(rate=2, scale=0.8, offset=0.1)


### EFFECTS ###
phaseEffect = audiofilters.Phaser(channel_count=1, sample_rate=44100)
pitchEffect = audiodelays.PitchShift(semitones=6, overlap=256, buffer_size=1024,channel_count=1,sample_rate=44100)#phaseEffect.frequency = synthio.LFO(offset=1000.0, scale=600.0, rate=0.5)
reverb = audiofreeverb.Freeverb(damp=0.3, buffer_size=1024, channel_count=1, sample_rate=44100, mix=0.4)
echo = audiodelays.Echo(max_delay_ms=1000, delay_ms=850, decay=0.65, buffer_size=1024, channel_count=1, sample_rate=44100, mix=0.7, freq_shift=False)

### Plug everything into output ###
phaseEffect.play(droneSynth)
reverb.play(phaseEffect)
echo.play(kickSynth)
pitchEffect.play(echo)


audio.play(mixer)
mixer.voice[0].play(pitchEffect)
mixer.voice[1].play(phaseEffect) #play phaseEffect or play reverb

##Enabling tremolo on the droneSynth
tremolo.scale = wavetable1.num_waves
droneSynth.blocks.append(tremolo)


#Setup of Sensors
i2c = busio.I2C(board.GP17,board.GP16)  # uses board.SCL and board.SDA  
mpu = adafruit_mpu6050.MPU6050(i2c)
mpr = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25) 


droneSynth.press(droneNote)
#synth.press(note1)
while True:
    kickSynth.press(kickNote)
    phaseEffect.frequency = synthio.LFO(offset=abs(mpu.acceleration[0]*100), scale=abs(mpu.acceleration[1])*10, rate=abs(mpu.acceleration[2])*2)#synthio.LFO(offset=abs(mpu.acceleration[0])*100, scale=abs(mpu.acceleration[2])*100, rate=abs(mpu.acceleration[1]))    
    wavetable1.wave_pos =  abs(mpu.gyro[0])*100
    wavetable2.wave_pos =  abs(mpu.gyro[1])*100
    tremolo.rate =  abs(mpr.pressure)/10 #what is this doing really?
    droneNote.bend = abs(mpr.pressure)/3000+0.2 ##or 2000
    #kickNote.bend = mpu.acceleration[1]*0.3
    pitchEffect.semitones= abs(mpu.gyro[1])
    #reverb.roomsize = 0.1+abs(mpr.pressure)/1000 # add reverb for more fun
    echo.mix = 1/abs(mpr.pressure/100)
    time.sleep(0.01)
    kickSynth.release(kickNote)
    time.sleep(0.1)
    #time.sleep(1/(mpr.pressure/200)) # makes it possible to control the rate of the pulse (BPM) using the pressure sensor's data - more pressure, faster rhythm
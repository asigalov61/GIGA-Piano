# -*- coding: utf-8 -*-
"""GIGA_Piano.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/asigalov61/GIGA-Piano/blob/main/GIGA_Piano.ipynb

# GIGA Piano (ver. 2.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

Credit for GPT2-RGA code used in this colab goes out @ Sashmark97 https://github.com/Sashmark97/midigen and @ Damon Gwinn https://github.com/gwinndr/MusicTransformer-Pytorch

***

WARNING: This complete implementation is a functioning model of the Artificial Intelligence. Please excercise great humility, care, and respect. https://www.nscai.gov/

***

#### Project Los Angeles

#### Tegridy Code 2022

***

# (Setup Environment)
"""

#@title nvidia-smi gpu check
!nvidia-smi

#@title Install all dependencies (run only once per session)

!git clone https://github.com/asigalov61/GIGA-Piano

!pip install torch

!pip install tqdm
!pip install matplotlib
!pip install torch-summary
!pip install sklearn
!pip install numpy

!apt install fluidsynth #Pip does not work for some reason. Only apt works
!pip install midi2audio

#@title Import all needed modules

print('Loading needed modules. Please wait...')
import os
import random
import copy

from collections import OrderedDict

from tqdm import tqdm

import matplotlib.pyplot as plt
import numpy as np

from torchsummary import summary
from sklearn import metrics

print('Loading core modules...')
os.chdir('/content/GIGA-Piano')

import TMIDIX
from GPT2RGAX import *

print('Loading aux modules...')

from midi2audio import FluidSynth
import librosa.display
from IPython.display import Audio, display

os.chdir('/content/')

print('Done!')
print('Enjoy!!')

"""# (MODEL LOAD)"""

# Commented out IPython magic to ensure Python compatibility.
#@title Unzip Pre-Trained GIGA Piano Models
# %cd /content/GIGA-Piano/Model

print('=' * 70)
print('Unzipping small pre-trained GIGA Piano model...Please wait...')

!cat GIGA_Piano_Trained_Model.zip* > GIGA-Piano-Trained-Model.zip
print('=' * 70)

!unzip -j GIGA-Piano-Trained-Model.zip
print('=' * 70)

print('Done! Enjoy! :)')
print('=' * 70)
# %cd /content/

# %cd /content/GIGA-Piano/Model/Large

print('=' * 70)
print('Unzipping large pre-trained GIGA Piano model...Please wait...')

!cat GIGA_Piano_Trained_Model.zip* > GIGA-Piano-Trained-Model.zip
print('=' * 70)

!unzip -j GIGA-Piano-Trained-Model.zip
print('=' * 70)

print('Done! Enjoy! :)')
print('=' * 70)
# %cd /content/

#@title Load/Reload the model


desired_model_to_load = "GIGA-Piano Large" #@param ["GIGA-Piano Large", "GIGA-Piano Small"]

if desired_model_to_load == 'GIGA-Piano Large':

  print('Loading Large GIGA-Piano model...')
  config = GPTConfig(128, 
                    1024,
                    dim_feedforward=1024,
                    n_layer=24, 
                    n_head=16, 
                    n_embd=1024,
                    enable_rpr=True,
                    er_len=1024)

  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

  model = GPT(config)

  state_dict = torch.load('/content/GIGA-Piano/Model/Large/GIGA_Piano_Trained_Model_1_epoch_60000_steps_0.9514_loss.pth', map_location=device)

  new_state_dict = OrderedDict()
  for k, v in state_dict.items():
      name = k[7:] #remove 'module'
      new_state_dict[name] = v

  model.load_state_dict(new_state_dict)

  model.to(device)

  model.eval()

  print('Done!')

  summary(model)

  cos_sim = metrics.pairwise.cosine_similarity(
      model.tok_emb.weight.detach().cpu().numpy()
  )
  plt.figure(figsize=(8, 8))
  plt.imshow(cos_sim, cmap="inferno", interpolation="none")
  im_ratio = cos_sim.shape[0] / cos_sim.shape[1]
  plt.colorbar(fraction=0.046 * im_ratio, pad=0.04)
  plt.xlabel("Position")
  plt.ylabel("Position")
  plt.tight_layout()
  plt.plot()
  plt.savefig("/content/GIGA-Piano-Large-Positional-Embeddings-Plot.png", bbox_inches="tight")

else:

  print('Loading Small GIGA-Piano model...')
  config = GPTConfig(128, 
                    1024,
                    dim_feedforward=1024,
                    n_layer=16, 
                    n_head=16, 
                    n_embd=1024,
                    enable_rpr=True,
                    er_len=1024)

  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

  model = GPT(config)

  state_dict = torch.load('/content/GIGA-Piano/Model/GIGA_Piano_Trained_Model_120000_steps_0.8075_loss.pth', map_location=device)

  new_state_dict = OrderedDict()
  for k, v in state_dict.items():
      name = k[7:] #remove 'module'
      new_state_dict[name] = v

  model.load_state_dict(new_state_dict)

  model.to(device)

  model.eval()

  print('Done!')

  summary(model)

  cos_sim = metrics.pairwise.cosine_similarity(
      model.tok_emb.weight.detach().cpu().numpy()
  )
  plt.figure(figsize=(8, 8))
  plt.imshow(cos_sim, cmap="inferno", interpolation="none")
  im_ratio = cos_sim.shape[0] / cos_sim.shape[1]
  plt.colorbar(fraction=0.046 * im_ratio, pad=0.04)
  plt.xlabel("Position")
  plt.ylabel("Position")
  plt.tight_layout()
  plt.plot()
  plt.savefig("/content/GIGA-Piano-Small-Positional-Embeddings-Plot.png", bbox_inches="tight")

"""# (GENERATE)

# Load Custom MIDI / MIDI seed
"""

#@title Custom MIDI option
full_path_to_custom_MIDI = "/content/GIGA-Piano/GIGA-Piano-Seed-1.mid" #@param {type:"string"}
simulated_or_constant_velocity = False #@param {type:"boolean"}

print('Loading custom MIDI file...')

#print('Loading MIDI file...')
score = TMIDIX.midi2ms_score(open(full_path_to_custom_MIDI, 'rb').read())

events_matrix = []

itrack = 1

while itrack < len(score):
    for event in score[itrack]:         
        if event[0] == 'note' and event[3] != 9:
            events_matrix.append(event)
    itrack += 1

# Sorting...
events_matrix.sort(key=lambda x: x[4], reverse=True)
events_matrix.sort(key=lambda x: x[1])

# recalculating timings
for e in events_matrix:
    e[1] = int(e[1] / 16)
    e[2] = int(e[2] / 32)

# final processing...

melody = []
melody_chords = []

pe = events_matrix[0]
for e in events_matrix:

    time = max(0, min(126, e[1]-pe[1]))
    dur = max(1, min(126, e[2]))

    ptc = max(1, min(126, e[4]))

    melody_chords.append([time, dur, ptc])

    if time != 0:
      if ptc < 60:
        ptc = (ptc % 12) + 60
      melody.append([time, dur, ptc])

    pe = e

inputs = []

for m in melody_chords:
  inputs.extend([127])
  inputs.extend(m)
  
inputs.extend([127])

print('Done!')

out1 = inputs

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pr_duration = song_f[-1][1]+song_f[-1][2]

pianoroll = [[0] * pr_duration for i in range(128)]

for s in song_f:
  for i in range(s[2]):
    try:
      pianoroll[s[4]][i+s[1]] = s[4]
    except:
      pass
  
piano_roll = np.array(pianoroll)

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=16, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
display(Audio(str(fname + '.wav'), rate=16000))

"""# Continuations"""

#@title Single Continuation Block Generator

#@markdown NOTE: Play with the settings to get different results

custom_MIDI_or_improvisation = True #@param {type:"boolean"}
number_of_prime_tokens = 256 #@param {type:"slider", min:32, max:512, step:8}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
number_of_batches = 2 #@param {type:"slider", min:1, max:8, step:1}
show_stats = True #@param {type:"boolean"}

#===================================================================
print('=' * 70)
print('GIGA Piano Music Model Continuation Generator')
print('=' * 70)

print('Generation settings:')
print('=' * 70)
print('Number of prime tokens:', number_of_prime_tokens)
print('Model temperature:', temperature)
print('Number of batches:', number_of_batches)
print('=' * 70)
print('Generating...')

if custom_MIDI_or_improvisation:
  inp = inputs[:number_of_prime_tokens+1]
else:
  inp = [127]

rand_seq = model.generate_batches(torch.Tensor(inp), 
                                          target_seq_length=1024,
                                          temperature=temperature,
                                          num_batches=number_of_batches,
                                          verbose=show_stats)
  
out1 = rand_seq[0].cpu().numpy().tolist()

print('Done!')

#@title Explore generated continuations
batch_number = 0 #@param {type:"slider", min:0, max:7, step:1}
simulated_or_constant_velocity = False #@param {type:"boolean"}

if batch_number >= number_of_batches:
  bn = 0
else:
  bn = batch_number

print('=' * 70)
print('Displaying batch #:',bn )
print('=' * 70)

out1 = rand_seq[bn].cpu().numpy().tolist()

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pr_duration = song_f[-1][1]+song_f[-1][2]

pianoroll = [[0] * pr_duration for i in range(128)]

for s in song_f:
  for i in range(s[2]):
    try:
      pianoroll[s[4]][i+s[1]] = s[4]
    except:
      pass
  
piano_roll = np.array(pianoroll)

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=16, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
display(Audio(str(fname + '.wav'), rate=16000))

#@title Multiple Continuation Blocks Generator

#@markdown NOTE: Play with the settings to get different results

custom_MIDI_or_improvisation = True #@param {type:"boolean"}
number_of_prime_tokens = 128 #@param {type:"slider", min:32, max:512, step:8}
number_of_continuation_blocks = 200 #@param {type:"slider", min:1, max:2000, step:1}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
simulated_or_constant_velocity = False #@param {type:"boolean"}
show_stats = False #@param {type:"boolean"}

#===================================================================
print('=' * 70)
print('GIGA Piano Music Model Continuation Generator')
print('=' * 70)

print('Generation settings:')
print('=' * 70)
print('Number of prime tokens:', number_of_prime_tokens)
print('Number of continuation blocks:', number_of_continuation_blocks)
print('Model temperature:', temperature)

print('=' * 70)
print('Generating...')

out1 = []

if custom_MIDI_or_improvisation:
  out1 = inputs[:number_of_prime_tokens]
  out1.extend([127])
else:
  out1.extend([127])

for i in tqdm(range(number_of_continuation_blocks)):

  rand_seq = model.generate(torch.Tensor(out1[-1021:]), 
                                            target_seq_length=len(out1[-1021:])+3,
                                            temperature=temperature,
                                            stop_token=127,
                                            verbose=show_stats)
    
  out = rand_seq[0].cpu().numpy().tolist()

  out1.extend(out[-3:])
  out1.extend([127])

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pr_duration = song_f[-1][1]+song_f[-1][2]

pianoroll = [[0] * pr_duration for i in range(128)]

for s in song_f:
  for i in range(s[2]):
    try:
      pianoroll[s[4]][i+s[1]] = s[4]
    except:
      pass
  
piano_roll = np.array(pianoroll)

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=16, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
display(Audio(str(fname + '.wav'), rate=16000))

"""# Inpainting / Controlled Generation"""

#@title Custom MIDI Inpaiting / Controlled Generator

#@markdown NOTE: Play with the settings to get different results

control_type = "Time" #@param ["Time", "Time-Duration"]
number_of_prime_notes = 8 #@param {type:"slider", min:1, max:128, step:1}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
simulated_or_constant_velocity = False #@param {type:"boolean"}
show_stats = False #@param {type:"boolean"}

#===================================================================
print('=' * 70)
print('GIGA Piano Music Model Inpainting / Controlled Generator')
print('=' * 70)

print('Generation settings:')
print('=' * 70)
print('Control type:', control_type)
print('Model temperature:', temperature)

print('=' * 70)
print('Generating...')

out1 = []

for m in melody_chords[:number_of_prime_notes]:
  out1.extend([127])
  out1.extend(m)
out1.extend([127])

if control_type == 'Time':
  ctrl = 1022
  out1.extend(melody_chords[number_of_prime_notes+1][:1])
else:
  ctrl = 1023
  out1.extend(melody_chords[number_of_prime_notes+1][:2])


for i in tqdm(range(number_of_prime_notes+2, len(melody_chords))):

  rand_seq = model.generate(torch.Tensor(out1[-ctrl:]), 
                                            target_seq_length=1024,
                                            temperature=temperature,
                                            stop_token=127,
                                            verbose=False)
    
  out = rand_seq[0].cpu().numpy().tolist()

  if control_type == 'Time':

    out1.extend(out[-2:])
    out1.extend([127])
    out1.extend(melody_chords[i][:1])
  else:
    out1.extend([out[-1]])
    out1.extend([127])
    out1.extend(melody_chords[i][:2])

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pr_duration = song_f[-1][1]+song_f[-1][2]

pianoroll = [[0] * pr_duration for i in range(128)]

for s in song_f:
  for i in range(s[2]):
    try:
      pianoroll[s[4]][i+s[1]] = s[4]
    except:
      pass
  
piano_roll = np.array(pianoroll)

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=16, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
display(Audio(str(fname + '.wav'), rate=16000))

#@title Alternative Custom MIDI Inpaiting / Controlled Generator

#@markdown NOTE: Play with the settings to get different results

control_type = "Time" #@param ["Time", "Time-Duration"]
number_of_prime_notes = 8 #@param {type:"slider", min:2, max:128, step:2}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
simulated_or_constant_velocity = False #@param {type:"boolean"}
show_stats = False #@param {type:"boolean"}

#===================================================================
print('=' * 70)
print('GIGA Piano Music Model Inpainting / Controlled Generator')
print('=' * 70)

print('Generation settings:')
print('=' * 70)
print('Control type:', control_type)
print('Model temperature:', temperature)

print('=' * 70)
print('Generating...')

out1 = []

for m in melody_chords[:number_of_prime_notes]:
  out1.extend([127])
  out1.extend(m)
out1.extend([127])

if control_type == 'Time':
  ctrl = 1022
  out1.extend(melody_chords[number_of_prime_notes+1][:1])
else:
  ctrl = 1023
  out1.extend(melody_chords[number_of_prime_notes+1][:2])


for i in tqdm(range(number_of_prime_notes+2, len(melody_chords)-2, 2)):

  rand_seq = model.generate(torch.Tensor(out1[-ctrl:]), 
                                            target_seq_length=1024,
                                            temperature=temperature,
                                            stop_token=127,
                                            verbose=False)
    
  out = rand_seq[0].cpu().numpy().tolist()

  if control_type == 'Time':

    out1.extend(out[-2:])
    out1.extend([127])
  else:
    out1.extend([out[-1]])
    out1.extend([127])

  out1.extend(melody_chords[i+1])
  out1.extend([127])

  if control_type == 'Time':
    out1.extend(melody_chords[i+2][:1])
  else:
    out1.extend(melody_chords[i+2][:2])


if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')
    
print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pr_duration = song_f[-1][1]+song_f[-1][2]

pianoroll = [[0] * pr_duration for i in range(128)]

for s in song_f:
  for i in range(s[2]):
    try:
      pianoroll[s[4]][i+s[1]] = s[4]
    except:
      pass
  
piano_roll = np.array(pianoroll)

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=16, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
display(Audio(str(fname + '.wav'), rate=16000))

"""# Melody Harmonization"""

#@title Melody Harmonization Generator

#@markdown NOTE: Play with the settings to get different results

number_of_prime_notes = 8 #@param {type:"slider", min:1, max:64, step:1}
number_of_notes_per_chord = 3 #@param {type:"slider", min:1, max:5, step:1}
random_number_of_notes_per_chord = False #@param {type:"boolean"}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
simulated_or_constant_velocity = False #@param {type:"boolean"}
show_stats = False #@param {type:"boolean"}


#===================================================================
print('=' * 70)
print('GIGA Piano Music Model Melody Harmonization Generator')
print('=' * 70)

print('Generation settings:')
print('=' * 70)
print('Number of prime notes:', number_of_prime_notes)
print('Model temperature:', temperature)
print('=' * 70)
print('Generating...')

inp = []

for i in range(number_of_prime_notes):
  inp.extend([127])
  inp.extend(melody[i])

for i in tqdm(range(number_of_prime_notes+1, len(melody))):

  inp.extend([127])
  inp.extend(melody[i])


  if random_number_of_notes_per_chord:
    nnpc = random.randint(1, number_of_notes_per_chord)
  else:
    nnpc = number_of_notes_per_chord

  for j in range(nnpc):
    inp.extend([127])
    inp.extend([0])
  
    rand_seq = model.generate(torch.Tensor(inp[-1022:]), 
                                              target_seq_length=1024,
                                              temperature=temperature,
                                              stop_token=127,
                                              verbose=show_stats)
      
    out = rand_seq[0].cpu().numpy().tolist()

    inp.extend(out[-2:])


out1 = inp

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pr_duration = song_f[-1][1]+song_f[-1][2]

pianoroll = [[0] * pr_duration for i in range(128)]

for s in song_f:
  for i in range(s[2]):
    try:
      pianoroll[s[4]][i+s[1]] = s[4]
    except:
      pass
  
piano_roll = np.array(pianoroll)

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=16, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
display(Audio(str(fname + '.wav'), rate=16000))

"""# Notes / Chords Progressions"""

#@title Notes Progressions Generator

#@markdown NOTE: Play with the settings to get different results
control_type = "Time" #@param ["Time", "Time-Duration"]
number_of_notes_to_generate = 300 #@param {type:"slider", min:10, max:5000, step:1}
desired_time = 8 #@param {type:"slider", min:1, max:127, step:1}
desired_duration = 7 #@param {type:"slider", min:1, max:127, step:1}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
simulated_or_constant_velocity = False #@param {type:"boolean"}
show_stats = False #@param {type:"boolean"}

#===================================================================
print('=' * 70)
print('GIGA Piano Music Model Notes Progressions Generator')
print('=' * 70)

print('Generation settings:')
print('=' * 70)
print('Control Type:', control_type)
print('Model temperature:', temperature)

print('=' * 70)
print('Generating...')

out1 = [127]

if control_type == 'Time':
  ctrl = 1022
  out1.extend([desired_time])

else:
  ctrl = 1023
  out1.extend([desired_time])
  out1.extend([desired_duration])

for i in tqdm(range(number_of_notes_to_generate)):

  rand_seq = model.generate(torch.Tensor(out1[-ctrl:]), 
                                            target_seq_length=1024,
                                            temperature=temperature,
                                            stop_token=127,
                                            verbose=show_stats)
    
  out = rand_seq[0].cpu().numpy().tolist()

  if control_type == 'Time':

    out1.extend(out[-2:])
    out1.extend([127])
    out1.extend([desired_time])

  else:
    out1.extend(out[-1:])
    out1.extend([127])
    out1.extend([desired_time])
    out1.extend([desired_duration])

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pr_duration = song_f[-1][1]+song_f[-1][2]

pianoroll = [[0] * pr_duration for i in range(128)]

for s in song_f:
  for i in range(s[2]):
    try:
      pianoroll[s[4]][i+s[1]] = s[4]
    except:
      pass
  
piano_roll = np.array(pianoroll)

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=16, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
display(Audio(str(fname + '.wav'), rate=16000))

#@title Chords Progressions Generator

#@markdown NOTE: Play with the settings to get different results
control_type = "Time" #@param ["Time", "Time-Duration"]
number_of_chords_to_generate = 40 #@param {type:"slider", min:10, max:200, step:1}
number_of_notes_per_chord = 3 #@param {type:"slider", min:1, max:5, step:1}
random_number_of_notes_per_chord = False #@param {type:"boolean"}
desired_time = 20 #@param {type:"slider", min:1, max:127, step:1}
desired_duration = 20 #@param {type:"slider", min:1, max:127, step:1}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
simulated_or_constant_velocity = False #@param {type:"boolean"}
show_stats = False #@param {type:"boolean"}

#===================================================================
print('=' * 70)
print('GIGA Piano Music Model Chords Progressions Generator')
print('=' * 70)

print('Generation settings:')
print('=' * 70)
print('Control Type:', control_type)
print('Model temperature:', temperature)

print('=' * 70)
print('Generating...')

out1 = [127]

if control_type == 'Time':
  ctrl = 1022
  out1.extend([desired_time])

else:
  ctrl = 1023
  out1.extend([desired_time])
  out1.extend([desired_duration])

nnpc = number_of_notes_per_chord

for i in tqdm(range(number_of_chords_to_generate)):

  rand_seq = model.generate(torch.Tensor(out1[-ctrl:]), 
                                            target_seq_length=1024,
                                            temperature=temperature,
                                            stop_token=127,
                                            verbose=show_stats)
    
  out = rand_seq[0].cpu().numpy().tolist()

  if control_type == 'Time':
    out1.extend(out[-2:])
    out1.extend([127])
  else:
    out1.extend(out[-1:])
    out1.extend([127])

  if random_number_of_notes_per_chord:
    nnpc = random.randint(1, number_of_notes_per_chord)

  for j in range(nnpc):
    out1.extend([0])

    if control_type == 'Time-Duration':
      out1.extend([desired_duration])

    rand_seq = model.generate(torch.Tensor(out1[-ctrl:]), 
                                          target_seq_length=1024,
                                          temperature=temperature,
                                          stop_token=127,
                                          verbose=show_stats)
  
    out = rand_seq[0].cpu().numpy().tolist()

    if control_type == 'Time':
        out1.extend(out[-2:])
        out1.extend([127])
    else:
      out1.extend(out[-1:])
      out1.extend([127])

  if control_type == 'Time':
    out1.extend([desired_time])

  else:
    out1.extend([desired_time])
    out1.extend([desired_duration])

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []

    song1 = []

    for s in song:
      if s != 127:
        son.append(s)

      else:
        if len(son) == 3:
          song1.append(son)
        son = []

    song2 = []
    cho = []
    for s in song1:
      if s[0] == 0:
        cho.append(s)
      else:
        song2.append(cho)
        cho = []
        cho.append(s)
    
    for s in song2:
      if len(s) > 0:

        channel = 0

        if simulated_or_constant_velocity:
          if len(s) == 1:
            vel = s[0][2] + 10
          else:
            vel = s[0][2] + 30
        else:
          vel = 90
        
        for ss in s:

          time += ss[0] * 16
              
          dur = ss[1] * 32
          
          pitch = ss[2]
                                    
          song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'GIGA Piano',  
                                                        output_file_name = '/content/GIGA-Piano-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

print('Displaying resulting composition...')
fname = '/content/GIGA-Piano-Music-Composition'

pr_duration = song_f[-1][1]+song_f[-1][2]

pianoroll = [[0] * pr_duration for i in range(128)]

for s in song_f:
  for i in range(s[2]):
    try:
      pianoroll[s[4]][i+s[1]] = s[4]
    except:
      pass
  
piano_roll = np.array(pianoroll)

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=16, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
display(Audio(str(fname + '.wav'), rate=16000))

"""# Congrats! You did it! :)"""
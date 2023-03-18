# import required libraries
from json.encoder import INFINITY
import sounddevice as sd
from scipy.io.wavfile import write, read
from tkinter import *
from tkinter import ttk
import tkinter as tk
import queue
import threading
from tkinter import messagebox
import soundfile as sf
# Spectrogram analysis libraries
import matplotlib.pyplot as plt
# from matplotlib.figure import Figure
from scipy import signal
from scipy.io import wavfile
import numpy as np
import librosa
import librosa.display
from pydub import AudioSegment
from functools import partial
import statistics as stats

# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

# Implementation using GUI as prototype 

# GUI part
stef_rec = Tk()
stef_rec.geometry("640x640")
stef_rec.title("Subaru WRX Audio Recording")
stef_rec.config(bg="#0000FF")
# the queue where the magic happens
q = queue.Queue()
# Input files to overlay
audio_f = StringVar()
noise_f = StringVar()
play_choice = StringVar()
name_test = StringVar()
# Global variable initialization
recording = False
file_exists = False
# Spectrogram analysis plot for original audio recording

def get_snr():
    # Get array of samples from the audio segmentation
    a_aud = read(audio_f.get())
    a_noi = read(noise_f.get())
    smth = np.array(a_aud[1],dtype=float)
    smth_noi = np.array(a_noi[1],dtype=float)
    # sample_rate, a_aud = wavfile.read(audio_f.get())
    # samp_r, a_noi = wavfile.read(noise_f.get())
    time = 10
    dubtime = time * 1000
    slice_aud = smth[:dubtime]
    slice_noi = smth_noi[:dubtime]
    overall = np.divide(np.abs(slice_aud), np.abs(slice_noi))
    overall[np.where(overall == INFINITY)] = 0
    snr = np.mean(overall)
    # snr2 = np.max(np.abs(slice_aud)) / np.max(np.abs(slice_noi))
    return print("SNR = %05f"%(snr))
    # return print("SNR = %05f dB"%(snr2))
    
def overlay():
    aud = AudioSegment.from_wav(audio_f.get())
    noi = AudioSegment.from_wav(noise_f.get())
    time = 10
    dubtime = time * 1000
    slice_aud = aud[:dubtime]
    slice_noi = noi[:dubtime]
    combo = slice_aud.overlay(slice_noi)
    totality = combo.export("wombocombo.wav", format="wav")

    # Plotting the spectrograms of each
    yaud, sraud = librosa.load(audio_f.get(), duration=time)
    ytot, srtot = librosa.load(totality, duration=time)

    fig, ax = plt.subplots(nrows=2, sharex=True)
    D_aud = librosa.stft(yaud, hop_length=128, n_fft=4096)
    Saud = librosa.amplitude_to_db(np.abs(D_aud), ref=np.max)
    img = librosa.display.specshow(Saud, hop_length=256, x_axis='time', y_axis='log',
                               ax=ax[0])
    ax[0].set(title='Ideal Speech - Middle Position')
    fig.colorbar(img, ax=ax[0], format="%+2.f dB")
    
    D_tot = librosa.stft(ytot, hop_length=128, n_fft=4096)
    S_tot = librosa.amplitude_to_db(np.abs(D_tot), ref=np.max)
    img = librosa.display.specshow(S_tot, hop_length=256, x_axis='time', y_axis='log',
                               ax=ax[1])
    ax[1].set(title='WomboCombo')
    fig.colorbar(img, ax=ax[1], format="%+2.f dB")

    return plt.show()

# Play the combo recording
def play_rec():
    data, fs = sf.read(file="wombocombo.wav", dtype='float64')
    sd.play(data, fs)
    sd.wait

def play_any():
    data, fs = sf.read(file=play_choice.get(), dtype="float64")
    sd.play(data, fs)
    sd.wait

# Amplitude analysis plot of original audio recording
def amp_plot(file_name):
    sample_rate, data = wavfile.read(file_name)
    duration = len(data)/sample_rate
    time = np.arange(0, duration, 1/sample_rate) #time vector
    plt.plot(time, data)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.title('Amplitude vs Time of Original Audio')
    plt.show()

def callback(indata, frams, time, status):
    q.put(indata.copy())

def threading_rec(x):
    # Recording button scenario
    if x == 1:
        t1 = threading.Thread(target = record)
        t1.start()
    elif x == 2:
        # Stopping the recording
        global recording
        recording = False
        messagebox.showinfo(message="Recording finished")
    
    # EXTRA STEP FOR AUDIO PLAYBACK
    elif x == 3:
        if file_exists:
            data, fs = sf.read(file=name_test.get(), dtype='float64')
            sd.play(data, fs)
            sd.wait
    elif x == 4:
        if file_exists:
            # spect_plot()
            messagebox.showinfo(message="Voila le Plot")
    elif x == 5:
        if file_exists:
            amp_plot(name_test.get())
            messagebox.showinfo(message="Voila l'amplitude")
    else:
        # Error or if nothing has been recorded
        messagebox.showerror(message="Let the music flow through the air")

def record():
    # Global variable to keep rec going
    global recording
    # Start recording
    recording = True
    global file_exists
    # Saving the audio recording to the name_test file
    messagebox.showinfo(message="Embarking on sound vibration hunting in momentural space and time")
    with sf.SoundFile(name_test.get(), mode='w', samplerate = 44100, channels=1) as file:
        # This is where the magic happens and no time needs to be specified for recording stream duration
        with sd.InputStream(samplerate=44100, channels=1, callback=callback):
            while recording == True:
                # Set file exists to true to allow playback part
                file_exists = True
                # Write our waves into le file
                file.write(q.get())

# Interactive buttons setup
# Label of app title
title_lbl  = Label(stef_rec, text="Subaru's WRX Audio Recorder", bg="#66CDAA", \
                        font=('Times New Roman', 20, 'bold')).grid(row=0, column=0, rowspan=1)
# Name the recording
name_test = Entry(stef_rec, textvariable=name_test)
# Insert Rec Name
test_name = Label(stef_rec, text="Insert Test Name:", font=('Times New Roman', 18))
# Rec Button
rec_btn = Button(stef_rec, text="Rec ON", command=lambda m=1:threading_rec(m))
# Stop Rec Button
stop_btn = Button(stef_rec, text="Rec OFF", command=lambda m=2:threading_rec(m))
# Playback Button
play_btn = Button(stef_rec, text="Play Recording", command=lambda m=3:threading_rec(m))
# Plot Spectrogram Button
plot_btn = Button(stef_rec, text="Plot Spectrogram", command=lambda m=4:threading_rec(m))
# Plot Amplitude Button
plotamp_btn = Button(stef_rec, text="Plot Amplitude", command=lambda m=5:threading_rec(m))
# Label Audio Testing Commands
test_label = Label(stef_rec, text="Test Audio Quality", bg="#66CDAA", font=('Times New Roman', 18))
# Overlay Ideal vs Noise Button
overlay_btn = Button(stef_rec, text="Overlay Audio with Noise", command=overlay)
# Input Audio Button
get_audio = Entry(stef_rec, textvariable=audio_f)
# Label Audio Input
audio_file = Label(stef_rec, text="Insert Audio File:", font=('Times New Roman', 18))
# Input Noise Button
get_noise = Entry(stef_rec, textvariable=noise_f)
# Label Noise Input
noise_file = Label(stef_rec, text="Insert Noise File:", font=('Times New Roman', 18))
# Play Combo button
play_combo = Button(stef_rec, text="Play Wombo Combo", command=play_rec)
# Play any file entry
play_what = Entry(stef_rec, textvariable=play_choice)
# Play any file button
play_anything = Button(stef_rec, text="Play Audio", command=play_any)
# Label to insert audio file to play
play_this = Label(stef_rec, text="Insert Audio to Play", font=('Times New Roman', 18))
# Print the SNR in the terminal
print_snr = Button(stef_rec, text="Print SNR of File", command=get_snr)


# Input file names
# entry1 = Entry(stef_rec, width = 20)
# entry1.focus_set()
# entry2 = Entry(stef_rec, width = 20)
# entry2.focus_set()
# entry1.pack()
# canvas1.create_window(200, 140, window=entry1)


# Positioning Setup
name_test.grid(row=1, column=1)
test_name.grid(row=1, column=0)
rec_btn.grid(row=2,column=1)
stop_btn.grid(row=3,column=1)
play_btn.grid(row=4,column=1)
plot_btn.grid(row=5, column=1)
plotamp_btn.grid(row=6, column=1)
test_label.grid(row=7, columns=3)
get_audio.grid(row=8, column=1)
audio_file.grid(row=8, column=0)
get_noise.grid(row=9, column=1)
noise_file.grid(row=9, column=0)
overlay_btn.grid(row=10, column=1)
play_combo.grid(row=11, column=1)
play_what.grid(row=12, column=1)
play_this.grid(row=12, column=0)
play_anything.grid(row=13, column=1)
print_snr.grid(row=14, column=1)


# Plot the spectrogram below the buttons
# plot_button = Button(master = stef_rec, 
#                      command = plt,
#                      height = 2, 
#                      width = 10,
#                      text = "Plot")
# plot_button.grid(row=5, column=1)
stef_rec.mainloop()

# --------------------------------------------------------------

# import wavio as wv

# MAKING THIS RUN WHILE THE REST OF PROGRAM IS ON
# Perhaps create a global boolean wherein it is true while the start button is clicked and then turnes false when the
# end button is pressed which then breaks the recording function

# Sampling frequency
# freq = 44100

# # Recording duration
# duration = 5

# # Start recorder with the given values
# # of duration and sample frequency
# recording = sd.rec(int(duration * freq),
# 				samplerate=freq, channels=1, dtype='float64')

# # Record audio for the given number of seconds
# sd.wait()

# # This will convert the NumPy array to an audio
# # file with the given sampling frequency
# write("audio_test1.wav", freq, recording)

# # Convert the NumPy array to audio file
# # wv.write("recording1.wav", recording, freq, sampwidth=2)


import numpy as np
import time, os, sys
from scipy.signal import hamming, resample

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../models/'))

import dftModel as DFT
import utilFunctions as UF
import math

def stftFiltering(x, fs, w, N, H, filter):
# Analysis/synthesis of a sound using the short-time fourier transform
# x: input sound, w: analysis window, N: FFT size, H: hop size
# filter: magnitude response of filter with frequency-magnitude pairs (in dB)
# returns y: output sound
	M = w.size                                     # size of analysis window
	hM1 = int(math.floor((M+1)/2))                 # half analysis window size by rounding
	hM2 = int(math.floor(M/2))                     # half analysis window size by floor
	x = np.append(np.zeros(hM2),x)                 # add zeros at beginning to center first window at sample 0
	x = np.append(x,np.zeros(hM1))                 # add zeros at the end to analyze last sample
	pin = hM1                                      # initialize sound pointer in middle of analysis window       
	pend = x.size-hM1                              # last sample to start a frame
	w = w / sum(w)                                 # normalize analysis window
	y = np.zeros(x.size)                           # initialize output array
	filt = np.interp(np.arange(N/2), (N/2)*filter[::2]/filter[-2], filter[1::2])  # generate filter shape
	while pin<=pend:                               # while sound pointer is smaller than last sample      
	#-----analysis-----  
		x1 = x[pin-hM1:pin+hM2]                      # select one frame of input sound
		mX, pX = DFT.dftAnal(x1, w, N)               # compute dft
	# filter
		mY = mX + filt                               # filter input magnitude spectrum
	#-----synthesis-----
		y1 = DFT.dftSynth(mY, pX, M)                # compute idft
		y[pin-hM1:pin+hM2] += H*y1                  # overlap-add to generate output sound
		pin += H                                    # advance sound pointer
	y = np.delete(y, range(hM2))                   # delete half of first window which was added in stftAnal
	y = np.delete(y, range(y.size-hM1, y.size))    # add zeros at the end to analyze last sample
	return y

def stftMorph(x1, x2, fs, w1, N1, w2, N2, H1, smoothf, balancef):
# morph of two sounds using the STFT
# x1, x2: input sounds, fs: sampling rate
# w1, w2: analysis windows, N1, N2: FFT sizes, H1: hop size
# smoothf: smooth factor for spectrum of sound 2
# balancef: balance between the 2 sounds, 0 is sound 1, 1 is sound 2
# returns y: output sound
	M1 = w1.size                                     # size of analysis window
	hM1_1 = int(math.floor((M1+1)/2))                # half analysis window size by rounding
	hM1_2 = int(math.floor(M1/2))                    # half analysis window size by floor
	L = int(x1.size/H1)
	x1 = np.append(np.zeros(hM1_2),x1)               # add zeros at beginning to center first window at sample 0
	x1 = np.append(x1,np.zeros(hM1_1))               # add zeros at the end to analyze last sample
	pin1 = hM1_1                                     # initialize sound pointer in middle of analysis window       
	w1 = w1 / sum(w1)                                # normalize analysis window
	M2 = w2.size                                     # size of analysis window
	hM2_1 = int(math.floor((M2+1)/2))                # half analysis window size by rounding
	hM2_2 = int(math.floor(M2/2))                    # half analysis window size by floor2
	H2 = int(x2.size/L)                              # hop size for second sound
	x2 = np.append(np.zeros(hM2_2),x2)               # add zeros at beginning to center first window at sample 0
	x2 = np.append(x2,np.zeros(hM2_1))               # add zeros at the end to analyze last sample
	pin2 = hM2_1                                     # initialize sound pointer in middle of analysis window  
	y = np.zeros(x1.size)                            # initialize output array
	for l in range(L):                                   
	#-----analysis-----  
		mX1, pX1 = DFT.dftAnal(x1[pin1-hM1_1:pin1+hM1_2], w1, N1)           # compute dft
		mX2, pX2 = DFT.dftAnal(x2[pin2-hM2_1:pin2+hM2_2], w2, N2)           # compute dft
	# morph
		mX2smooth = resample(np.maximum(-200, mX2), mX2.size*smoothf)       # smooth spectrum of second sound
		mX2 = resample(mX2smooth, N2/2) 
		mY = balancef * mX2 + (1-balancef) * mX1                            # generate output spectrum
	#-----synthesis-----
		y[pin1-hM1_1:pin1+hM1_2] += H1*DFT.dftSynth(mY, pX1, M1)  # overlap-add to generate output sound
		pin1 += H1                                     # advance sound pointer
		pin2 += H2                                     # advance sound pointer
	y = np.delete(y, range(hM1_2))                   # delete half of first window which was added in stftAnal
	y = np.delete(y, range(y.size-hM1_1, y.size))    # add zeros at the end to analyze last sample
	return y

# example call of stftMorph function
if __name__ == '__main__':
	(fs, x1) = UF.wavread('../../sounds/ocean.wav')
	(fs, x2) = UF.wavread('../../sounds/speech-male.wav')
	w1 = np.hamming(1024)
	N1 = 1024
	H1 = 256
	w2 = np.hamming(1024)
	N2 = 1024
	smoothf = .5
	balancef = 0.2
	y = stftMorph(x1, x2, fs, w1, N1, w2, N2, H1, smoothf, balancef)

	w = np.hamming(1024)
	N = 1024
	H = 256
	filter = np.array([0,0, 500, 0, 5000,-20, 6000,-40, 22050,-100])
	y = stftFiltering(y, fs, w, N, H, filter)
	UF.play(y, fs)

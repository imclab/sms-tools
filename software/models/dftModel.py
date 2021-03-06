import matplotlib.pyplot as plt
import numpy as np
import time, os, sys
from scipy.fftpack import fft, ifft
import math
import utilFunctions as UF

def dftModel(x, w, N):
# Analysis/synthesis of a signal using the discrete fourier transform
# x: input signal, w: analysis window, N: FFT size, 
# returns y: output signal

  hN = N/2                                                # size of positive spectrum
  hM1 = int(math.floor((w.size+1)/2))                     # half analysis window size by rounding
  hM2 = int(math.floor(w.size/2))                         # half analysis window size by floor
  fftbuffer = np.zeros(N)                                 # initialize buffer for FFT
  y = np.zeros(x.size)                                    # initialize output array
  #----analysis--------
  xw = x*w                                                # window the input sound
  fftbuffer[:hM1] = xw[hM2:]                              # zero-phase window in fftbuffer
  fftbuffer[N-hM2:] = xw[:hM2]        
  X = fft(fftbuffer)                                      # compute FFT
  mX = 20 * np.log10(abs(X[:hN]))                         # magnitude spectrum of positive frequencies in dB     
  pX = np.unwrap(np.angle(X[:hN]))                        # unwrapped phase spectrum of positive frequencies
  #-----synthesis-----
  Y = np.zeros(N, dtype = complex)                        # clean output spectrum
  Y[:hN] = 10**(mX/20) * np.exp(1j*pX)                    # generate positive frequencies
  Y[hN+1:] = 10**(mX[:0:-1]/20) * np.exp(-1j*pX[:0:-1])   # generate negative frequencies
  fftbuffer = np.real(ifft(Y))                            # compute inverse FFT
  y[:hM2] = fftbuffer[N-hM2:]                             # undo zero-phase window
  y[hM2:] = fftbuffer[:hM1]
  return y

def dftAnal(x, w, N):
# Analysis of a signal using the discrete fourier transform
# x: input signal, w: analysis window, N: FFT size, 
# returns mX: magnitude spectrum, pX: phase spectrum

  hN = N/2                                  # size of positive spectrum
  hM1 = int(math.floor((w.size+1)/2))       # half analysis window size by rounding
  hM2 = int(math.floor(w.size/2))           # half analysis window size by floor
  fftbuffer = np.zeros(N)                   # initialize buffer for FFT
  w = w / sum(w)                            # normalize analysis window
  xw = x*w                                  # window the input sound
  fftbuffer[:hM1] = xw[hM2:]                # zero-phase window in fftbuffer
  fftbuffer[N-hM2:] = xw[:hM2]        
  X = fft(fftbuffer)                       # compute FFT
  mX = 20 * np.log10(abs(X[:hN]))          # magnitude spectrum of positive frequencies in dB     
  pX = np.unwrap(np.angle(X[:hN]))         # unwrapped phase spectrum of positive frequencies
  return mX, pX

def dftSynth(mX, pX, M):
# Synthesis of a signal using the discrete fourier transform
# mX: magnitude spectrum, pX: phase spectrum, M: window size
# returns y: output signal

  N = mX.size*2
  hN = N/2                                                # size of positive spectrum
  hM1 = int(math.floor((M+1)/2))                          # half analysis window size by rounding
  hM2 = int(math.floor(M/2))                              # half analysis window size by floor
  fftbuffer = np.zeros(N)                                 # initialize buffer for FFT
  y = np.zeros(M)                                         # initialize output array
  Y = np.zeros(N, dtype = complex)                        # clean output spectrum
  Y[:hN] = 10**(mX/20) * np.exp(1j*pX)                    # generate positive frequencies
  Y[hN+1:] = 10**(mX[:0:-1]/20) * np.exp(-1j*pX[:0:-1])   # generate negative frequencies
  fftbuffer = np.real(ifft(Y))                            # compute inverse FFT
  y[:hM2] = fftbuffer[N-hM2:]                             # undo zero-phase window
  y[hM2:] = fftbuffer[:hM1]
  return y


# example call of dftAnal and dftSynth function
if __name__ == '__main__':
  (fs, x) = UF.wavread('../../sounds/oboe-A4.wav')
  w = np.blackman(511)
  N = 1024
  pin = 5000
  hM1 = int(math.floor((w.size+1)/2)) 
  hM2 = int(math.floor(w.size/2))  
  x1 = x[pin-hM1:pin+hM2]
  mX, pX = dftAnal(x1, w, N)
  y = dftSynth(mX, pX, w.size)*sum(w)

  plt.figure(1, figsize=(9.5, 7))
  plt.subplot(4,1,1)
  plt.plot(np.arange(-hM1, hM2), x1)
  plt.axis([-hM1, hM2, min(x1), max(x1)])
  plt.ylabel('amplitude')
  plt.title('input signal: x')

  plt.subplot(4,1,2)
  plt.plot(np.arange(N/2), mX, 'r')
  plt.axis([0,N/2,min(mX),max(mX)])
  plt.title ('magnitude spectrum: mX')
  plt.ylabel('amplitude (dB)')
  plt.ylabel('frequency samples')

  plt.subplot(4,1,3)
  plt.plot(np.arange(N/2), pX, 'c')
  plt.axis([0,N/2,min(pX),max(pX)])
  plt.title ('phase spectrum: pX')
  plt.ylabel('phase (radians)')
  plt.ylabel('frequency samples')

  plt.subplot(4,1,4)
  plt.plot(np.arange(-hM1, hM2), y)
  plt.axis([-hM1, hM2, min(y), max(y)])
  plt.ylabel('amplitude')
  plt.title('output signal: y')

  plt.tight_layout()
  plt.show()

  error = -(20*np.log10(2**15) - 20*np.log10(sum(abs(x1*w-y))))
  print "output/input error (in dB) =", error

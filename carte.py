# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 17:40:53 2019

@author: Alexis

This files gives a few function for signal processoring and displayng

"""

import numpy as np
import math

import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.mlab as mlab

# makes a spectogram
def getFreqArray(data, freqS, fenetre, minFreq, maxFreq):
    '''renvoie la carte temps-fréquence. sous la forme (temps, frequences, mesures[temps][freq])
    Prend en argumant un couple du type (timestamps, datas) où timestamp et data sont des listes
    fenetre est la taille de la fenetre temporel prise autour du temps pour le calcule de la fft
    freqS est la fréquence à laquelle il faut faire des fft sur le signal '''
    fen = fenetre/2
    freqE = len(data[0])/(data[0][-1] - data[0][0])
    n = int(fenetre*freqE)
    t = np.arange(data[0][0] + fen, data[0][-1] - fen, 1./freqS)
    buffer = np.zeros((len(t),n))
    l = [0 for _ in range(len(t))]
    for i in range(len(data[0])):
        for a in range(len(t)):
            if l[a] < n and (t[a] - fen < data[0][i] or n-l[a] >= len(data[0])-i):
                buffer[a, l[a]] = data[1][i]
                l[a] += 1
    freq = np.fft.rfftfreq(n, 1./freqE)
    fmin = 0
    fmax = 0
    for i in freq:
        if i > minFreq:
            break
        fmin += 1
    for i in freq:
        fmax += 1
        if i > maxFreq:
            break
    return (t, freq[fmin:fmax], abs(np.fft.rfft(buffer, norm = 'ortho'))[:,fmin:fmax])

#display spectogram
def specto(data, minFreq = 5, maxFreq = 40):
    fig, ax = plt.subplots(figsize=(10,6))
    Pxx = spectoArray(data)
    im = ax.imshow(Pxx, interpolation = 'spline16', extent = (0, 2, minFreq, maxFreq), origin = 'lower')
    ax.set_aspect(aspect = 0.7*2/35)
    fig.colorbar(im)
    return Pxx


def spectoArray(data, minFreq = 5, maxFreq = 40):
    Pxx, freqs, bins = mlab.specgram(data, NFFT=200, Fs=500, noverlap=180, mode = 'magnitude')
    fmin = 0
    fmax = 0
    for i in freqs:
        if i > minFreq:
            break
        fmin += 1
    for i in freqs:
        fmax += 1
        if i > maxFreq:
            break
    Pxx = Pxx[fmin:fmax,:]
    return Pxx
        
def getCarteElec(data, freqS, fenetre, minFreq, maxFreq, elec):
    return getFreqArray((data[0], data[elec]), freqS, fenetre, minFreq, maxFreq)[2].flatten()

def getCarte(data, freqS, fenetre, minFreq, maxFreq):
    ''' renvoie la carte temps-fréquence, à partir de la donné enregistrée'''
    return np.array([getFreqArray((data[0], data[i]), freqS, fenetre, minFreq, maxFreq)[2].flatten() for i in range(1,9) ]).flatten()

def drawFreqArray(carte):
    m = carte[2].max()
    
    fig, ax = plt.subplots()
    X,Y = np.meshgrid(carte[0], carte[1])
    levels = np.arange(0, m, m/1000.)
    norm = col.Normalize(0, m)
    contour = ax.contourf(X,Y, carte[2].transpose(), levels = levels, norm = norm)
    fig.colorbar(contour)
    ax.set_xlabel("temps")
    ax.set_ylabel("fréquence")
    
    return fig

def imshowFreqArray(carte):
    fig, ax = plt.subplots(figsize=(10,6))
    Pxx = carte[2]
    freq = carte[1]
    im = ax.imshow(Pxx.transpose(), interpolation = 'spline16', extent = (0, 2, freq[0], freq[-1]), origin = 'lower')
    ax.set_aspect(aspect = 0.7*2/35)
    fig.colorbar(im)

def drawElectrode(data, elec, freqS, fenetre, minFreq = 5, maxFreq = 40):
    f = getFreqArray((data[0],data[elec]),freqS, fenetre, minFreq, maxFreq)
    drawFreqArray(f)
    
def filtreMoyen(data, fenetre):
    '''écart à la moyenne sur la fenetre de fenetre points. data est un array ou une liste monodimensionnelle '''
    fenetre = fenetre//2
    S = sum(data[0:fenetre])
    nb = fenetre
    N = len(data)
    filtrer = np.empty(len(data))
    for i in range(N):
        if i - fenetre >= 0:
            S -= data[i-fenetre]
            nb -= 1
        if i + fenetre < N:
            S += data[i+fenetre]
            nb += 1
        filtrer[i] = data[i] - S/nb
    return filtrer

def recentrage(data , fen = 0):
    M = sum(data)/len(data)
    return data - M*np.ones(data.shape)
    
def Invfft(freq, data, t):
    return [ sum([data[i]*math.sin(2*np.pi*freq[i]*j) for i in range(len(freq)) ]) for j in t ]
    
def CompareEle(db, i, elec):
    a = db.loadedSignal[i].data
    b = moy(filtreMoyen(a[elec], 100), 10)
    #b = recentrage(a[elec], 100)
    plt.subplots()
    plt.plot(a[0], a[elec])
    plt.subplots()
    plt.plot(a[0], b)
    
    fig, ax = plt.subplots()
    
    freq = np.fft.rfftfreq(len(a[elec]), 1./500.)
    fmin = 0
    fmax = 0
    for i in freq:
        if i > 5:
            break
        fmin += 1
    for i in freq:
        fmax += 1
        if i > 40:
            break
    plt.plot(np.fft.rfftfreq(len(a[elec]), 1/500.)[fmin:fmax], abs(np.fft.rfft(a[elec], norm = 'ortho'))[fmin:fmax], label = 'non filtré')
    #plt.subplots()
    plt.plot(np.fft.rfftfreq(len(b), 1/500.)[fmin:fmax], abs(np.fft.rfft(b, norm = 'ortho'))[fmin:fmax], label = 'filtré')
    ax.legend()
    
    drawFreqArray(getFreqArray((a[0], a[elec]), 10, 0.5, 5, 40))
    drawFreqArray(getFreqArray((a[0], b),       50, 0.5, 5, 40))
    
def moy(data, fenetre):
    '''convolution'''
    fenetre = fenetre//2
    S = sum(data[0:fenetre])
    nb = fenetre
    N = len(data)
    filtrer = np.empty(len(data))
    for i in range(N):
        if i - fenetre >= 0:
            S -= data[i-fenetre]
            nb -= 1
        if i + fenetre < N:
            S += data[i+fenetre]
            nb += 1
        filtrer[i] = S/nb
    return filtrer
    
def filtreSignal(s, fenetreLine, fenetreMoy = 10):
    '''applique le filtreMoyen pour supprimer les déviation linéaire et recentrer avec suppression des bords pour éviter les déviations
    puis moyenne pour couper la fréquence 50Hz'''
    return np.array( [s[0]] +
                    [moy(filtreMoyen(s[i], fenetreLine), fenetreMoy) for i in range(1, 9)])
    

    
    
    
    
    
    
    
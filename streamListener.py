# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 13:06:26 2018

@author: Alexis

Classes to retrieve information from the stream
"""


from pylsl import StreamInlet, resolve_stream
from collections import deque

import threading as th
import numpy as np     
import time as t       #needed for fps
import streamError

mutex = th.Lock()

class StreamListener:
    '''Permet l'écoute pour des protocole asynchrone'''
    def __init__(self, streamName, streamType, maxData):
        self.streamName = streamName
        self.streamType = streamType
        self._deque = deque([], maxData)
        self._inlet = None
        self._continue = False
        self._innerBuffer = np.empty((0,0))
        self._buffer = np.empty((0,0))
        self.treatment = None
        self._frames = deque([])
        
    def connect(self):
        '''Connecte le stream listener au stream vérifaint streamType et streamName.
        Renvoie si un stream à été trouvé. Peut lever une NameError
        Conçu en reprenant le code du groupe de PSC précédent'''
        streams = resolve_stream('type', self.streamType)
        for stream in streams: #cherche parmi les flux arrivant celui qui vient de NIC
            if (stream.name() == self.streamName):
                self._inlet = StreamInlet(stream, max_buflen = 1) #garde le stream en mémoire dans "inlet"
                return True
        return False
        
    def actualizeData(self):
        '''récupère les nouvelles données.'''
        if(self._inlet == None):
            raise streamError.UnConnctedStreamError(" récupérer des donneés ")        
        while True and self._continue:    
            sample,  timestamp = self._inlet.pull_sample(0.0) #8 éléctrodes + timestamp
            if(sample == None):
                break
            sample.insert(0, timestamp)
            self._deque.append(sample)
            
    def mainloop(self):
        while self._continue:
            self.actualizeData()
            self._makeBuffer()
            self._treatBuffer()
            self._buffer = self._innerBuffer
            self._frames.append(t.time())
            while( len(self._frames) > 0 and self._frames[-1] - self._frames[0] > 1.0):
                self._frames.popleft()
            #print(len(self._frames))
    
    def start(self):
        if self._continue == False:
            self._continue = True
            th.Thread(target = self.mainloop).start()
        
    def stop(self):
        self._continue = False
        
    def _makeBuffer(self):
        if len(self._deque) == 0:
            self._innerBuffer = np.empty((0,0))
            return
        buffer = np.empty((len(self._deque[0]), len(self._deque)))
        i = 0
        for s in self._deque:
            j = 0
            for x in s:
                buffer[j, i] = x
                j += 1
            i += 1
        self._innerBuffer = buffer
    
    def _treatBuffer(self):
        if self.treatment != None:
            self._innerBuffer = self.treatment.apply(self._innerBuffer)
        
    def getBuffer(self):
        return self._buffer
    
    def fps(self):
        return len(self._frames)
        
        
class FftListener(StreamListener):
    '''ajoute le buffer des fft'''
    def __init__(self, streamName, streamType, maxData):
        StreamListener.__init__(self, streamName, streamType, maxData)
        
        self._activatefft = False
        self._bufferFFT = np.empty((0,0))
        self.channel_d = 0
        self.channel_f = 0
        self.n = 0
        self.T = 0
    
    def activateFFT(self, channel_d, channel_f, n, T):
        '''Les voies sur lesquelles est faite la  fft sont [channel_d, channel_f[
        n désigne le nombre de données sur l'axe à utiliser
        T désignne la période d'échantillonage '''
        self.channel_d = channel_d
        self.channel_f = channel_f
        self.n = n
        self.T = T
        self._activatefft = True

    def desactivateFFT(self):
        self._activatefft = False
        self._bufferFFT = np.empty((0,0))
        
    def getFFTBuffer(self):
        return self._bufferFFT
    
    def _treatBuffer(self):
        StreamListener._treatBuffer(self)
        if self._activatefft:
            self._bufferFFT = np.concatenate((np.array([np.fft.fftfreq(self.n, self.T)]), 
                                              np.fft.fft(self._innerBuffer[self.channel_d:self.channel_f], 
                                                         self.n, 
                                                         norm="ortho") ))
    
'''A stream listener that calls the machine learning engine once the buffer is updated'''    
class MLlistener(StreamListener):
    def __init__(self, streamName, streamType, maxData):
        StreamListener.__init__(self, streamName, streamType, maxData)
        self.ml = None
        self.mPoint = 50
        self.g = None
        self.maxData = maxData
        
    def linkMl(self, ml):
        self.ml = ml
        
    def _treatBuffer(self):
        if len(self._innerBuffer[0]) == self.maxData:
            m = self.ml.predict(self._innerBuffer)*2 - 1
            ti = t.time()
            mutex.acquire()
            for g in self.g:
                g.appendData(ti, m)
            mutex.release()
            t.sleep(0.10)
            
            
    def linkGraph(self, g):
        self.g = g
        
        
        
        
        
        
        
        
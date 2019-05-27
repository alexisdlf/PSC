# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 22:07:08 2018

@author: Alexis
"""

from pylsl import StreamInlet, resolve_streams

import streamError
import threading as th
import numpy as np
import time
import math
from collections import deque

from databaseManager import Signal #pour SignalRecorder


class StreamRecorder:
    def __init__(self, streamName, streamType):
        self._inlet = None
        self._recording = False
        self._recordlength = 0
        self.ts = 0
        self.offset = 0
        self._buffer = None
        self.streamType = streamType
        self.streamName = streamName
        self.th = th.Thread()
        
        self._deque = deque([])
        self._fps = deque([])
        
    def connect(self):
        '''Connecte le stream listener au stream vérifaint streamType et streamName.
        Renvoie si un stream à été trouvé. Peut lever une NameError
        Conçu en reprenant le code du groupe de PSC précédent'''
        streams = resolve_streams()
        for stream in streams: #cherche parmi les flux arrivant celui qui vient de NIC
            if (stream.name() == self.streamName and stream.type() == self.streamType):
                self._inlet = StreamInlet(stream, 3) #garde le stream en mémoire dans "inlet"
                self.offset = time.time() - self._inlet.pull_sample()[1]
                return True
        return False
    
    def isRecording(self):
        return self._recording
    
    def getRecord(self):
        if(self.isRecording()):
            raise streamError.RecordingSreamError()
        else:
            return self._buffer
        
    def getBuffer(self):
        return self._buffer
        
    def bufferAvailable(self):
        if self._buffer == None:
            return False
        return True
    
    def startRecord(self, ts, length):
        '''lance un enregistrement de t seconde dans un thread séparé'''
        if self._recording:
            raise streamError.RecordingSreamError()
        if self._inlet == None:
            raise streamError.UnConnctedStreamError("enregistrement")
        self._recording = True
        self._recordlength = length
        self.ts = ts
        self.th = th.Thread(target = self._record)
        self.th.start()
    
    def _record(self):
        times = []
        samples = []
        while self._recording:
            s,t = self._inlet.pull_chunk(0.0)
            i = len(t) - 1
            i2 = 0
            if i >= 0 and t[i] + self.offset >= self.ts:
                while i - i2 > 1:
                    med = t[math.ceil((i + i2)/2)] + self.offset
                    if med > self.ts:
                        i = (i + i2)//2
                    else:
                        i2 = math.ceil((i + i2)/2)
                times += t[i:]
                samples += s[i:]
                break
            time.sleep(0.2)
        while self._recording:
            s, t = self._inlet.pull_chunk(0.0)
            if len(t) and t[-1] + self.offset >= self.ts + self._recordlength:
                i = len(t) - 1
                i2 = 0
                while i - i2 > 1:
                    med = t[math.ceil((i + i2)/2)] + self.offset
                    if med > self.ts + self._recordlength:
                        i = (i + i2)//2
                    else:
                        i2 = math.ceil((i + i2)/2)
                times += t[:i]
                samples += s[:i]
                break
            else:
                times += t
                samples += s
            time.sleep(0.2)
        self._buffer = np.concatenate((np.array([times]) + (self.offset - self.ts), np.array(samples).T ))
        self._recording = False
        
    def stopRecord(self):
        self._recording = False
        if self.th:
            while self.th.is_alive():
                time.sleep(0.01)
        self._buffer = None
            
    def listen(self, nbData):
        self.stopRecord()
        self._deque = deque([], nbData)
        self._recording = True
        self.th = th.Thread(target = self.mainloop).start()
        
    def mainloop(self):
        while self._recording:
            self._actualizeData()
            self._makeBuffer()
            self._fps.append(time.time())
            while( len(self._fps) > 0 and self._fps[-1] - self._fps[0] > 1.0):
                self._fps.popleft()  
        
    def _actualizeData(self):
        '''récupère les nouvelles données.'''
        if(self._inlet == None):
            raise streamError.UnConnctedStreamError(" récupérer des donneés ")        
        while True:
            sample,  timestamp = self._inlet.pull_sample(0.0) #8 éléctrodes + timestamp
            if(sample == None):
                break
            sample.insert(0, timestamp)
            self._deque.append(sample)     
        
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
        self._buffer = buffer
            
class SignalRecorder(StreamRecorder):
    def __init__(self, streamName, streamType):
        StreamRecorder.__init__(self, streamName, streamType)
        self.info = None
    def startRecordSignal(self, ts, length, info):
        self.info = info.copy()
        self.startRecord(ts, length)
    def getSignal(self):
        return Signal(self.getRecord(), self.info)
            
class QualitySignalRecorder(SignalRecorder):
    def __init__(self, streamName, streamType, streamTypes):
        SignalRecorder.__init__(self, streamName, streamType)
        self.info = None
        self._qualities = [StreamRecorder(streamName, s) for s in streamTypes]
    def startRecordSignal(self, ts, length, info):
        SignalRecorder.startRecordSignal(self, ts, length, info)
        for s in self._qualities:
            s.startRecord(ts, length)
    def stopRecord(self):
        SignalRecorder.stopRecord(self)
        for s in self._qualities:
            s.stopRecord()
    def connect(self):
        b = SignalRecorder.connect(self)
        for s in self._qualities:
            s.connect()
        return b
    def getSignal(self):
        return Signal(self.getRecord(), self.info, [s.getRecord() for s in self._qualities])
    
    def isRecording(self):
        for s in self._qualities:
            if s.isRecording():
                return True
        return StreamRecorder.isRecording(self)
            
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
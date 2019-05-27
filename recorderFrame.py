# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 11:43:34 2019

@author: Alexis
"""

import tkinter as tk

import threading as th
import time
import random as rd

from gtts import gTTS
from pygame import mixer

    
class RecorderFrame(tk.Frame):
    def __init__(self, master, stream, db, protocole, user, session, callback = None):
        tk.Frame.__init__(self, master)
        self.processing = tk.BooleanVar()
        self.processing.set(False)
        
        self.buffer1 = None
        self.buffer2 = None
        self.buffer3 = None
        self._toSave = None
        
        self.strEtat = tk.StringVar()
        self.strButton = tk.StringVar()
        self.strLast = tk.StringVar()
        
        self.dataMgr = db
        self.prot = protocole
        self.str = stream
        self.user = user
        self.session = session
        self.expes = self.prot.expe
                
        self.callback = None
        try:
            mixer.init()
        except:
            pass
        
        self.protocole = self.prot.num
        self.tempsRepos = self.prot.tempsRepos
        
        self.strEtat.set("Initialisation")
        self.labelEtat = tk.Label(master = self, textvariable=self.strEtat, relief = tk.GROOVE,
                             padx = 20, pady = 20)
        self.labelEtat.grid(row = 0, column = 0, padx = 50, pady = 50)
        
        self.lblFrDernier = tk.LabelFrame(master = self, text = "dernier :")
        self.lblFrDernier.grid(row = 0, column = 1, padx = 20, pady = 20)
        
        self.strLast.set("")
        self.labelLast = tk.Label(master = self.lblFrDernier, textvariable = self.strLast)
        self.labelLast.grid(row = 0, column = 0, padx = 10, pady = 10)
                
        buttonCancel = tk.Button(master = self.lblFrDernier, text="Annuler dernier enregistrement",
                                 command = self.annuler)
        buttonCancel.grid(row = 1, column = 0, padx = 10, pady = 10)
                
        self.strButton.set("Pause")
        self.buttonPause = tk.Button(master = self, textvariable=self.strButton, padx = 10, pady = 10, 
                                     command=self.switch)
        self.buttonPause.grid(row = 1, column = 1)
                
    def setSound():
        tts = gTTS("arrêtez", 'fr')
        tts.save("obj/stop.mp3")
        tts = gTTS("Les expériences vont commencer dans 5 secondes.", 'fr')
        tts.save("obj/instructionDebut.mp3")
        tts = gTTS("reprise dans 5 secondes", 'fr')
        tts.save("obj/instructionReprise.mp3")
        
    def prepare():
        mixer.init()
        try:
            mixer.music.load("obj/instructionDebut.mp3")
            mixer.music.load("obj/stop.mp3")
            mixer.music.load("obj/instructionReprise.mp3")
        except:
            RecorderFrame.setSound()
            
    def commencer(self):
        self.buffer1 = None
        self.buffer2 = None
        self.buffer3 = None
        self._toSave = None
        mixer.music.load("obj/instructionDebut.mp3")
        mixer.music.play()
        self.processing.set(True)
        self.strEtat.set("En marche")
        self.procede()
    
    def annuler(self):
        self.strLast.set("")
        self.buffer1 = None
        self.buffer2 = None
        self.buffer3 = None
        self._toSave = None
        
    def switch(self, evt = None):
        if self.processing.get() or evt != None:
            self.processing.set(False)
            self.str.stopRecord()
            self.strButton.set("Reprendre")
            self.strEtat.set("En pause")
        else:
            self.buffer1 = None
            self.buffer2 = None
            self.buffer3 = None
            self._toSave = None
            self.str.stopRecord()
            mixer.music.load("obj/instructionReprise.mp3")
            mixer.music.play()
            self.processing.set(True)
            self.strEtat.set("En marche")
            th.Thread(target=self.procede).start()
            self.strButton.set("Pause")
            
    def arreter(self):
        self.processing.set(False)
        self.str.stopRecord()
            
    def randExpe(self):
        return self.expes[rd.randint(0, len(self.expes)-1)]
        
    def saveBuffer(self):
        if self._toSave and self._toSave.info:
            self.dataMgr.saveSignal(self._toSave)
    
    def procede(self):
        phase = 1
        e = None
        info = {}
        info["protocole"] = self.protocole
        info["sujet"] = self.user
        info["session"] = self.session
        while self.processing.get() and mixer.music.get_busy():
            time.sleep(0.1)
        t = time.time()
        while time.time() - t < 5:
            time.sleep(0.1)
        
        while self.processing.get():
            if phase == 1:
                if self.str.isRecording():
                    time.sleep(0.01)
                else:
                    e = self.randExpe()
                    mixer.music.load(e.getText())
                    mixer.music.play()
                    info["categorie"] = e.getCategorie()
                    phase = 2
            
            if phase == 2:
                if mixer.music.get_busy():
                    time.sleep(0.01)
                else:
                    self._toSave = self.buffer3
                    self.buffer3 = self.buffer2
                    self.buffer2 = self.buffer1
                    self.buffer1 = self.str.getSignal()
                    self.str.startRecordSignal(time.time(), e.getTime(), info)
                    th.Thread(target = self.saveBuffer).start()
                    self.strLast.set(e.getCategorie())
                    phase = 3
                
            if phase == 3:
                if self.str.isRecording():
                    time.sleep(0.01)
                else:
                    mixer.music.load("obj/stop.mp3")
                    mixer.music.play()
                    info["categorie"] = "attente"
                    phase = 4
                
            if phase == 4:
                if mixer.music.get_busy():
                    time.sleep(0.01)
                else:
                    self._toSave = self.buffer3
                    self.buffer3 = self.buffer2
                    self.buffer2 = self.buffer1
                    self.buffer1 = self.str.getSignal()
                    if self.callback != None:
                        self.callback(self.buffer1)
                    self.str.startRecordSignal(time.time(), self.tempsRepos, info)
                    th.Thread(target = self.saveBuffer).start()
                    phase = 1
        print("end thread")
            
            
            
            
            
            
            
            
            
            
            
            
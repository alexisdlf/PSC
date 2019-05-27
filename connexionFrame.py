# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 11:26:00 2019

@author: Alexis
"""

import tkinter as tk
import tkinter.messagebox as msgBox 
import streamRecorder as sr


class ConnexionFrame(tk.Frame):
    def __init__(self, master, streamName, streamType, qualityStreams = []):
        tk.Frame.__init__(self, master)
        
        self.connected = tk.BooleanVar()
        self.connected.set(False)
        
        self.str = sr.QualitySignalRecorder(streamName, streamType, qualityStreams)
        
        frCo = tk.Frame(master = self)
        frCo.grid(row = 0, column = 0, ipadx = 10, ipady = 10)
        frCo.rowconfigure(1, weight = 1)
        
        frEl = tk.Frame(master = self)
        frEl.grid(row = 0, column = 1, ipadx = 10, ipady= 10)
        
        
        self.co = tk.StringVar()
        self.co.set("Le casque n'est pas encore connecté")
        labelCo = tk.Label(master = frCo, textvariable = self.co, relief = tk.GROOVE, padx = 20, pady = 20)
        labelCo.grid(row = 0, column = 0, columnspan = 2)
        
        labelEx = tk.Label(master = frCo, text = "pour connecter le casque, brancher les \n électrodes" + 
                                                       "au boitier, allumer le boitier \n et NIC, puis appuyer " + 
                                                       "sur le boutton connecter ci-dessous")
        labelEx.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = "s")
        
        
        
        buttonCo = tk.Button(master = frCo, text = "connecter", command = self.connect)
        buttonCo.grid(row = 1, column = 1, padx = 10, pady = 10, ipadx = 10, ipady = 10, sticky = "s")
        
    def connect(self):
        if not self.connected.get():
            self.connected.set(self.str.connect())
        if self.connected.get():
            self.co.set("Casque connecté")
        else:
            self.co.set("Le casque n'est pas encore connecté")
            msgBox.showerror("Connexion échoué", 
                             "La tentative de connexion a échoué, vérifiez les branchements et réessayez")
    
    def isConnected(self):
        return self.connected.get()
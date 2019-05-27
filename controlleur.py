# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 23:49:30 2019

@author: Alexis

The class used to controll the arm (real one or simulated with Bras.py) using neuroGraph decisions
"""

import tkinter as tk
import time
from bras import Bras
from pygame import mixer
from arduino import Arduino

def funcInc(n):
    return 0.12*n/(15 + n)

class Controlleur(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.bras = Bras(self)
        self.bras.grid(row = 2, column = 0, columnspan = 10)
        
        self.decider = None
        
        self.buttonMove = tk.Button(self, text = 'move', command = self.move, repeatinterval = 20, repeatdelay = 200)
        self.buttonMove.grid(row = 3, column = 0)
        
        self.buttonNext = tk.Button(self, text = 'attraper', command = self.attraper, repeatinterval = 20, repeatdelay = 500)
        self.buttonNext.grid(row = 3, column = 1)
        
        self.buttonSens = tk.Button(self, text = 'ouvrir', command = self.ouvrir, repeatinterval = 20, repeatdelay = 500)
        self.buttonSens.grid(row = 3, column = 2)
        
        self.state = None
        self.resetTimer = 2.5
        self.changeTime = time.time()
        
        mixer.init()
        self.sound = mixer.Sound("obj/pat.wav")
        
        self.sens = 1
        self.n = 0
        
        self.bras.info = "Calcule : attraper\nMouvement : mouvement"
        self.bras.nextArt()
        
    def setDecider(self, decider):
        self.decider = decider
        self.decider.grid(row = 0, column = 0, columnspan = 10)
        
    def appendData(self, x, y):
        self.decider.appendData(x, y)
        if self.isBlocked():
            return
        if self.decider.getState() == 1:
            self.attraper()
            time.sleep(1)
            self.ouvrir()
        elif self.decider.getState() == -1:
            self.move()
        else:
            self.n = 0
        
    def move(self):
        self.n += 1
        self.bras.increment = funcInc(self.n)*self.sens
        self.bras.move()
        
    def nextArt(self):
        self.bras.nextArt()
        self.changeTime = time.time()
    
    def swapSens(self):
        self.sens *= -1
    
    def isBlocked(self):
        return time.time() - self.changeTime < self.resetTimer
        
    def attraper(self):
        self.changeTime = time.time()
        self.sound.play()
        self.bras.attraper()
    
    def ouvrir(self):
        self.bras.ouvrir()
    
#de 0 à 180 -> déplacement du coude
#181 = ouverture, 182 = fermeture
class ArduinoControl(Controlleur):
    def __init__(self, master, port):
        Controlleur.__init__(self, master)
        self.arduino = Arduino("COM3")
    
    def move(self):
        Controlleur.move(self)
        #gestion du sens 
        if self.bras.coude_o < 0:
            self.bras.coude_o = 0
            self.swapSens()
        if self.bras.coude_o > 3.14:
            self.bras.coude_o = 3.14
            self.swapSens()
        self.arduino.sendInt(int(self.bras.coude_o*180/3.1416))
        
    def attraper(self):
        Controlleur.attraper(self)
        self.arduino.sendInt(182)
        
    def ouvrir(self):
        Controlleur.ouvrir(self)
        self.arduino.sendInt(181)
        
        
        
        
    
        
        
        
        
        
        
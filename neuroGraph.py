from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

from tkinter import Frame, Label, StringVar
import tkinter as tk

from collections import deque

import streamListener as sl

class AnimatedGraph(Frame):
    def __init__(self, master, label1, label2, figsize=(10,2), dpi=100):
        Frame.__init__(self, master)
        self.fig = Figure(figsize=figsize, dpi=dpi)
        self.axes = self.fig.add_subplot(1,1,1)
        self.line, = self.axes.plot([], [])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self) #Widget Tk permettant d'afficher des graphes matplotlib
        self.canvas.get_tk_widget().grid(row = 0, column = 1, rowspan = 3, sticky= 'nesw', ipadx = 0, ipady = 0, padx = 0, pady = 0)
        self.rowconfigure(1,weight=1) #pour que les lignes/colones se redimensionnne
        self.columnconfigure(0,weight=1)
        self.label1 = Label(self, text = label1, borderwidth = 2, relief = tk.GROOVE)
        self.label1.grid(row = 0, column = 0, sticky = 'ne',ipadx = 5, ipady = 5)
        self.label2 = Label(self, text = label2, borderwidth = 2, relief = tk.GROOVE)
        self.label2.grid(row = 2, column = 0, sticky = 'se', ipadx = 5, ipady = 5)
        
        self.textInfo = StringVar()
        self.textInfo.set("donnée brut")
        self.info = Label(self, textvariable = self.textInfo)
        self.info.grid(row = 1, column = 0)
        
        self.ani = None
        self.x = None
        self.ya = None
        self.y = None
        self.state = 0
        
    def _initFig(self):
        self.line.set_ydata([])
        self.line.set_xdata([])
        return self.line,
        
    def draw(self, i):  
        sl.mutex.acquire()
        self.line.set_ydata(self.ya.copy())
        self.line.set_xdata([self.x[i] - self.x[-1] for i in range(len(self.ya))])
                
        if self.state == 1:
            self.label1["background"] = 'red'
            self.label2["background"] = 'light grey'
        elif self.state == -1:
            self.label1["background"] = 'light grey'
            self.label2["background"] = 'green'
        else:
            self.label1["background"] = 'light grey'
            self.label2["background"] = 'light grey'
        
        sl.mutex.release()
        return self.line, 
            
    def setUp(self, size):
        self.x = deque([], size)
        self.y = deque([], size)
        self.ya = deque([], size)
        
        self.axes.set_ybound(-1, 1)
        self.axes.set_xbound(-5, 0.1)
        
    def start(self, interval):
        self.ani = animation.FuncAnimation(self.fig, self.draw, init_func=self._initFig, 
                                           interval=interval, blit=True, repeat=True)
        
    def decide(self):
        return 0
    
    def appendData(self, x, y):
        self.x.append(x)
        self.y.append(y)
        self.ya.append(self.analize())
        self.state = self.decide()

    def analize(self):
        return self.y[-1]
    
    def getState(self):
        return self.state
    
class Intergrateur(AnimatedGraph):
    def __init__(self, master, t, seuil = 0.95, label1 = 'calcule', label2 = 'mouvement', figsize=(10,2), dpi=100):
        AnimatedGraph.__init__(self, master, label1, label2, figsize, dpi)
        self.t = t
        self.seuil = seuil
        self.textInfo.set("Moyenne sur " + str(t) + " s\n" + "Seuil à " + str(seuil))
        
    def analize(self):
        xa = [self.y[i]*(self.x[i] - self.x[i-1]) for i in range(1, len(self.y)) if self.x[-1] - self.x[i] < self.t]
        return sum(xa)/self.t
    
    def decide(self):
        if len(self.ya) == 0:
            return 0
        if self.ya[-1] > self.seuil:
            return 1
        if self.ya[-1] < -self.seuil:
            return -1
        return 0
    
    def setUp(self, size):
        AnimatedGraph.setUp(self, size)
        self.axes.axhline(self.seuil, linewidth = 0.2)
        self.axes.axhline(-self.seuil, linewidth = 0.2)
    
class Plateau(AnimatedGraph):
    def __init__(self, master, t, seuil, perc, label1 = 'calcule', label2 = 'mouvement', figsize=(10,2), dpi=100):
        AnimatedGraph.__init__(self, master, label1, label2, figsize, dpi)
        self.t = t
        self.seuil = seuil
        self.perc = perc
        self.textInfo.set("Reconnaissance de plateau sur " + str(t) + " s\n" + "Seuil à " + str(perc) + 
                          "% au dessus de " + str(seuil))

        
    def analize(self):
        y = self.y[-1]
        if y > self.seuil:
            self.y[-1] = 1
        elif y < -self.seuil:
            self.y[-1] = -1
        else:
            self.y[-1] = 0
        return y
    
    def decide(self):
        xa = [self.y[i]*(self.x[i] - self.x[i-1]) for i in range(1, len(self.y)) if self.x[-1] - self.x[i] < self.t]
        x = sum(xa)/self.t
        if x > self.seuil:
            return 1
        if x < -self.seuil:
            return -1
        return 0
    
    def setUp(self, size):
        AnimatedGraph.setUp(self, size)
        self.axes.axhline(self.seuil, linewidth = 0.2)
        self.axes.axhline(-self.seuil, linewidth = 0.2)
    
class IntegrateurAsymetrique(Intergrateur):
    def __init__(self, master, t, seuil1, seuil2, label1 = 'calcule', label2 = 'mouvement', 
                 figsize=(10,2), dpi=100):
        Intergrateur.__init__(self, master, t, 1, label1, label2, figsize, dpi)
        self.seuil1 = seuil1
        self.seuil2 = seuil2
        
    def decide(self):
        if len(self.ya) == 0:
            return 0
        if self.ya[-1] > self.seuil1:
            return 1
        if self.ya[-1] < -self.seuil2:
            return -1
        return 0
    
    def setUp(self, size):
        AnimatedGraph.setUp(self, size)
        self.axes.axhline(self.seuil1, linewidth = 0.2)
        self.axes.axhline(-self.seuil2, linewidth = 0.2)        


class Asym(AnimatedGraph):
    def __init__(self, master, dec1, dec2, figsize=(10,2), dpi=100):
        self.d1 = dec1
        self.d2 = dec2
        AnimatedGraph.__init__(self, master, self.d1.label1["text"], self.d2.label2["text"], figsize, dpi)
        self.d1.line, = self.axes.plot([], [], color = 'r')
        self.d2.line, = self.axes.plot([], [], color = 'g')
        self.d1.fig = self.fig
        self.d2.fig = self.fig
        self.d1.axes = self.axes
        self.d2.axes = self.axes
        self.d1.label1 = self.label1
        self.d2.label2 = self.label2
        
    def setUp(self, size):
        AnimatedGraph.setUp(self.d1, size)
        AnimatedGraph.setUp(self.d2, size)
        
        self.axes.axhline(self.d1.seuil, linewidth = 0.2)
        self.axes.axhline(-self.d2.seuil, linewidth = 0.2)   
    
    
    def start(self, interval):
        self.ani1 = animation.FuncAnimation(self.d1.fig, self.d1.draw, init_func=self._initFig, 
                                           interval=interval, blit=False, repeat=True)
        self.ani2 = animation.FuncAnimation(self.d2.fig, self.d2.draw, init_func=self._initFig, 
                                           interval=interval, blit=False, repeat=True)
        
    def decide(self):
        if self.d1.getState() == 1:
            return 1
        elif self.d2.getState() == -1:
            return -1
        return 0
    
    def appendData(self, x, y):
        self.d1.appendData(x, y)
        self.d2.appendData(x, y)
        self.state = self.decide()

    def analize(self):
        return 0
    
    def getState(self):
        return self.state
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 12:11:39 2019

@author: Alexis

The main file : start the user interface to record or test machine learning predictions
"""

import tkinter as tk
import tkinter.messagebox as msgBox 

import threading as th
import os
import pickle
import random as rd
import time
import math

import databaseManager as db
import protocole as p

from selectUserFrame import SelectUserFrame
from recorderFrame import RecorderFrame
from connexionFrame import ConnexionFrame
from streamListener import MLlistener
from neuroGraph import AnimatedGraph, Intergrateur, Plateau, IntegrateurAsymetrique, Asym
from controlleur import Controlleur, ArduinoControl

from Machine_learning_avec_filtrage import Machine_learning_avec_filtrage, Machine_learning_sans_filtrage


def save_obj(obj, name ): #copied form stack overflow
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ): #copied form stack overflow
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


"""Two classes to fake a stream or a machine learning engine to test the rest of the code """
class FakeStream:
    def __init__(self):
        self.i = time.time()
    def pull_sample(self, timeout = 0):
        if time.time() - self.i > 0.1:
            self.i += 0.002
            return [int(self.i*e%2) for e in range(8)], self.i
        else:
            return None, None
    def pull_chunk(self, timeout = 0):
        self.i += 3
        return [list(range(1,9)) for i in range(3)], [self.i + j - 3 for j in range(3)]

class FakeMl:
    def __init__(self, db, user):
        pass
    def predict(self, signal):
        #return math.sin(time.time())/2 + 0.5
        return rd.random()


class NeuroApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Neurofeedback")
        self.root.resizable(True, True)
        self.root.columnconfigure(0, weight = 1)
        self.root.columnconfigure(1, weight = 1)
        self.root.rowconfigure(0, weight = 1)
        
        self.database = db.DatabaseManager("data/enregistrements/", "data/table.db")
        self.prot = p.court
        self.sl = None
        self.user = ""
        self.session = -1
        self.ml = None
        self.looping = False
        self.reFr = None
        self.th = None
        self.electrode = 1
        self.bars = []
        
        self.cheating = False
        
    def mainWindow(self):
        self.suFr = SelectUserFrame(self.root, "users")
        self.suFr.grid(row = 0, column = 0)
        
        self.connFr = ConnexionFrame(self.root, 'NIC', 'EEG', ["Quality"])
        self.connFr.grid(row = 0, column = 1)
        
        self.buttonFrame = tk.Frame(self.root)
        self.buttonFrame.grid(row = 1, column = 0, columnspan = 10)
        
        self.buttonRecord = tk.Button(self.buttonFrame, text= "Acquisition", command=self.goRecord)
        self.buttonRecord.grid(row = 0, column = 0, padx = 10)

        self.buttonCheat = tk.Button(self.buttonFrame, text = "cheat", command=self.cheat)
        self.buttonCheat.grid(row = 7, column = 0)
        
        #self.buttonTest = tk.Button(self.buttonFrame, text = "Tester", command=self.goTest)
        #self.buttonTest.grid(row = 0, column = 1, padx = 10)
        
        self.buttonDemo = tk.Button(self.buttonFrame, text = "Demo", command = self.goDemo)
        self.buttonDemo.grid(row = 0, column = 2, padx = 10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
    def close(self):
        self.root.quit()
        self.root.destroy()
        self.sl.stop()
        
    def cheat(self, evt=None):
        self.connFr.str._inlet = FakeStream()
        self.connFr.connected.set(True)
        self.connFr.co.set("casque connecté")
        self.cheating = True
        
    def goRecord(self, evt=None):
        if not self.suFr.validate():
            return
        self.user = self.suFr.getUser()
        self.session = self.suFr.getSession()
        if not self.connFr.isConnected():
            msgBox.showerror("Casque non connecté", "Le casque n'est pas connecter")
            return
        self.sl = self.connFr.str
                
        self.suFr.destroy()
        self.connFr.destroy()
        self.buttonFrame.destroy()
        
        self.recordWindow()
        
    def goTest(self, evt=None):
        if not self.suFr.validate():
            return
        self.user = self.suFr.getUser()
        self.session = self.suFr.getSession()
        if not self.connFr.isConnected():
            msgBox.showerror("Casque non connecté", "Le casque n'est pas connecter")
            return
        
        self.sl = MLlistener('NIC', 'EEG', 1000)
        self.sl._inlet = self.connFr.str._inlet
        self.setMl()
        self.sl.linkMl(self.ml)
        
        self.suFr.destroy()
        self.connFr.destroy()
        self.buttonFrame.destroy()
        
        self.testWindow()
    
    def goDemo(self, evt=None):
        if not self.suFr.validate():
            return
        self.user = self.suFr.getUser()
        self.session = self.suFr.getSession()
        if not self.connFr.isConnected():
            msgBox.showerror("Casque non connecté", "Le casque n'est pas connecter")
            return
        
        self.sl = MLlistener('NIC', 'EEG', 1000)
        self.sl._inlet = self.connFr.str._inlet
        self.setMl()
        self.sl.linkMl(self.ml)
        
        self.suFr.destroy()
        self.connFr.destroy()
        self.buttonFrame.destroy()
        
        self.demoWindow()
    
    def setMl(self):
        if self.ml != None:
            return
        if self.cheating:
            self.ml = FakeMl(self.database, 'o')
            return
        print("loading...")
        self.database.load('''SELECT * FROM mesures WHERE (categorie = 'calcul mental' OR categorie = 'mouvement imaginé') ''')
        print(str(len(self.database.loadedSignal.keys())) + " signal loaded")
        print("filtering...")
        self.ml = Machine_learning_avec_filtrage(self.database)
        print("signals filtered")
        print("treating...")
        self.ml.treat("carte", 0)
        print("signal treated")
        print('training...')
        self.ml.train_interface('lda')
        print("pret")
        
            
    def goMainFromRecord(self, evt = None):
        self.sl.stopRecord()
        while self.th.is_alive():
            time.sleep(0.1)
        self.th = None
        self.buttonRetour.destroy()
        self.reFr.arreter()
        time.sleep(2)
        self.reFr.destroy()
        self.sl.stopRecord()
        self.mainWindow()
    
    def goMainFromTest(self):
        self.sl.stop()
        for g in self.bars:
            g.destroy()
        self.buttonRetour.destroy()
        
        self.mainWindow()
    
    def recordWindow(self):
        self.reFr = RecorderFrame(self.root, self.sl, self.database, self.prot, self.user, self.session, self.dumb)
        self.reFr.grid()
        self.buttonRetour = tk.Button(self.reFr, text = 'stop', command = self.goMainFromRecord)
        self.buttonRetour.grid(row = 1, column = 0)
        self.th = th.Thread(target=self.reFr.commencer)
        self.th.start()
        
    def testWindow(self):
        
        self.buttonRetour = tk.Button(self.root, text = 'stop', command = self.goMainFromTest)
        self.buttonRetour.grid(row = 100, column = 0)
        
        self.bars = []
        self.bars.append(AnimatedGraph(self.root, 'calcule', 'mouvement'))
        self.bars.append(Intergrateur(self.root, 2, 0.9))
        self.bars.append(Intergrateur(self.root, 3, 0.9))
        for i in range(len(self.bars)):
            self.bars[i].setUp(50)
            self.bars[i].grid(row = i, column = 0, sticky = 'nesw', pady = 10)
            self.bars[i].start(50)
                
        self.sl.linkGraph(self.bars)
        self.sl.start()

    def demoWindow(self):
        self.buttonRetour = tk.Button(self.root, text = 'stop', command = self.goMainFromTest)
        self.buttonRetour.grid(row = 100, column = 0)
        
        self.bars = []
        self.bars.append(AnimatedGraph(self.root, 'calcule', 'mouvement'))
        self.bars[0].setUp(50)
        self.bars[0].grid(row = 0, column = 0, sticky = 'nesw', pady = 10)
        self.bars[0].start(50)
        
        #self.con = ArduinoControl(self.root, 'COM3')
        self.con = Controlleur(self.root)
        self.con.setDecider(IntegrateurAsymetrique(self.con, 3, 0.6, 0.92))
        self.con.decider.setUp(50)
        self.con.decider.start(50)
        self.con.grid()
        
        self.bars.append(self.con)
        
        self.sl.linkGraph(self.bars)
        self.sl.start()
        
        def draw():
            self.con.bras.draw()
            if self.sl._continue:
                self.root.after(100, draw)
        
        self.root.after(100, draw)
    
    def dumb(self):
        pass
        
    def prepare():
        try:
            os.makedirs("obj")
        except:
            pass
        try:
            os.makedirs("data/enregistrements")
        except:
            pass
        try:
            open("obj/users.pkl", 'r')
        except:
            users = {'Pierre BERTRAND': 0, 
                     'Julien DESCAMPS': 0, 
                     'Alexis de LA FOURNIERE': 0, 
                     'Ahmed BENNANI': 0}
            save_obj(users, "users")
        try:
            open("obj/last_protocole.pkl", 'r')
        except:
            b = "1.1.0"
            save_obj(b, "last_protocole")
        d = db.DatabaseManager("data/enregistrements/", "data/table.db")
        d.createMesureTable()
        d.createExperienceTable()
        d.createPlacementTable()
        d.createProtocoleTable()
        for pr in p.protos.values():
            d.saveProtocole(pr)
            pr.install()
            print(pr.num + " ok")
        RecorderFrame.prepare()
        
    def start(self):
        self.mainWindow()
        self.root.mainloop()
        
        
        
        
        
        
        
        
        
        
        
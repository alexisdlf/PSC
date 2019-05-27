# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 10:59:06 2019

@author: Alexis
"""

import tkinter as tk
import tkinter.messagebox as msgBox 
import pickle

def save_obj(obj, name ): #copied form stack overflow
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ): #copied form stack overflow
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

class SelectUserFrame(tk.Frame):
    def __init__(self, master, file = ""):
        tk.Frame.__init__(self, master)
        self.file = file
        
        self.users = {}
        try:
            self.users = load_obj(file)
        except:
            pass
        
        self.labelUser = tk.Label(master = self, text = "Choisissez l'utilisateur")
        self.labelUser.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
        
        self.user = tk.StringVar()
        if(self.getUser()):
            self.user.set(self.getUser())
        else:
            self.user.set("")
        self.entryUser = tk.Entry(master = self, textvariable = self.user, width = 50)
        self.entryUser.grid(row = 1, column = 0, columnspan = 1, padx = 10, pady = 10)
        
        self.listUser = tk.Listbox(master = self, selectmode=tk.BROWSE, activestyle=tk.DOTBOX, 
                                   selectbackground = "white", selectforeground = "black", width = 50)        
        for i in self.users.keys():
            if i != "current":
                self.listUser.insert(tk.END, i)
                
        
        self.listUser.bind('<ButtonRelease-1>', self._newUser)
        self.listUser.grid(row = 2, column = 0, padx = 10, pady = 10)
        
        self.buttonSuppr = tk.Button(master = self, text="Supprimer", command=self._suppr, width = 10)
        self.buttonSuppr.grid(row = 1, column = 1, padx = 10, pady = 10)
        
    def getUser(self):
        if("current" in self.users):    
            return self.users["current"]
        return None
    
    def getSession(self):
        a = self.getUser()
        if a!= None:
            return self.users[a]
        return 0
    
    def _suppr(self):
        if(self.listUser.curselection() and self.listUser.get(self.listUser.curselection()) == self.user.get()):
            if(self.users[self.user.get()] == 0):
                self.users.pop(self.user.get())
            self.user.set("")
            self.listUser.delete(self.listUser.curselection())
                
    def _newUser(self, evt):
            if(self.listUser.curselection()):
                self.user.set(self.listUser.get(self.listUser.curselection()) )
    
    def validate(self, evt = None):
        if(self.user.get() == "current" or self.user.get() == ""):
            msgBox.showerror("Donnee invalide", "Le nom d'utilisateur est invalide")
            return False
        else:
            if(not self.user.get() in self.users.keys()):
                self.users[self.user.get()] = 0
            else:
                self.users[self.user.get()] += 1
            self.users["current"] = self.user.get()
            self.save()
            return True
    
    def save(self):
        if len(self.file):
            save_obj(self.users, self.file)
    
    
    
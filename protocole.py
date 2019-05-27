# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 23:47:12 2019

@author: Alexis
"""

import random as rd
import experiences as e
import os

class protocole:
    def __init__(self):
        self.expe = []
        self.tempsRepos = 0
        self.electrodes = ["" for i in range(8)]
        self.num = "0.0.0"
    def install(self):
        for ex in self.expe:
            try:
                os.makedirs(ex.folder)
            except:
                pass
            ex.install()
            print(ex.categorie + " ok")
    def randExpe(self):
        return self.expe[rd.randint(len(self.expe))]

court = protocole()
court.num = "2.0.0"
court.tempsRepos = 2
court.electrodes = ["FC5", "CP5", "C3", "C1", "C2", "C4", "CP6", "FC6"]
court.expe = [e.Calcule("obj/2.0.0/calcule", 2, 10, 20),
              e.Mvmt("obj/2.0.0/mvmt", 2)]

protos = {"2.0.0" : court}
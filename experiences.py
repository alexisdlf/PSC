# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 17:26:17 2018

@author: Alexis
"""

import random as rd
from gtts import gTTS

class Experience:
    def __init__(self, folder, temps):
        self.categorie = "non définie"
        self.time = temps
        self.folder = folder
    def getText(self):
        pass
    def getCategorie(self):
        return self.categorie
    def getTime(self):
        return self.time
    def install(self):
        pass
    
    
class Calcule(Experience):
    def __init__(self, folder, temps, a, b):
        Experience.__init__(self, folder, temps)
        self.categorie = "calcul mental"
        self.a = a
        self.b = b
    def getText(self):
        return self.folder + "/" + str(rd.randint(0,(self.b-self.a)**2-2)) + ".mp3"
    def install(self):
        for i in range(self.a, self.b):
            for j in range(self.a, self.b):
                try:
                    open(str(self.folder) + "/" + str(i-self.a +(self.b-self.a)*(j-self.a)) + ".mp3")
                except:
                    gTTS(str(i) + " fois " + str(j), 'fr').save(str(self.folder) + "/" + str(i-self.a +(self.b-self.a)*(j-self.a)) + ".mp3")
    def getTexts(self):
        return [str(self.folder) + "/" + str(i) + ".mp3" for i in range((self.b-self.a)**2-1)]
    
        
class Rimes(Experience):
    def __init__(self, folder, temps, l):
        Experience.__init__(self, folder, temps)
        self.categorie = "rimes"
        self.mots = l
    def getText(self):
        return self.folder + "/" + self.mots[rd.randint(0,len(self.mots)-1)] + ".mp3"
    def install(self):
        for i in self.mots:
            try:
                open(self.folder + "/" + str(i) + ".mp3")
            except:
                gTTS("trouvez des mots qui riment avec " + str(i), 'fr').save(self.folder + "/" + str(i) + ".mp3")

class MvmtLongIm(Experience):
    def __init__(self, folder, temps, par):
        Experience.__init__(self, folder, temps)
        self.categorie = "mouvement long " + par + " imaginé"
        self.par = par
    def getText(self):
        return self.folder + "/son.mp3"
    def install(self):
        try:
                open(self.folder + "/son.mp3")
        except:
            gTTS("imaginez un mouvement continue de votre " + self.par, 'fr').save(self.folder + "/son.mp3")

class MvmtBrefIm(Experience):
    def __init__(self, folder, temps, par):
        Experience.__init__(self, folder, temps)
        self.categorie = "mouvement bref " + par + " imaginé"
        self.par = par
    def getText(self):
        return self.folder + "/son.mp3"
    def install(self):
        try:
            open(self.folder + "/son.mp3")
        except:
            gTTS("imaginez un mouvement bref de votre " + self.par, 'fr').save(self.folder + "/son.mp3")
    
class MvmtBrefReel(Experience):
    def __init__(self, folder, temps, par):
        Experience.__init__(self, folder, temps)
        self.categorie = "mouvement bref " + par + " réel"
        self.par = par
    def getText(self):
        return self.folder + "/son.mp3"
    def install(self):
        try:
            open(self.folder + "/son.mp3")
        except:
            gTTS("faites un mouvement bref avec votre " + self.par, 'fr').save(self.folder + "/son.mp3")

class Mvmt(Experience):
    def __init__(self, folder, temps):
        Experience.__init__(self, folder, temps)
        self.categorie = "mouvement imaginé"
    def getText(self):
        return self.folder + "/son.mp3"
    def install(self):
        try:
            open(self.folder + "/son.mp3")
        except:
            gTTS("mouvement", 'fr').save(self.folder + "/son.mp3")
    def getTexts(self):
        return [self.folder + "/son.mp3"]









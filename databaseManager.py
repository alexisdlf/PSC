# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 17:31:25 2018

@author: Alexis
"""

import sqlite3
from datetime import datetime
from numpy import array
import sys

from protocole import protocole
from experiences import Experience

class UndocumentedSignalError(Exception):
    def __init__(self, undoc):
        self.undoc = undoc
    def __str__(self):
        return "tentative de sauvegarde d'un signal ou " + self.undoc + " n'est pas renseigné"



class Signal:
    ''' Classe représentant une mesure. data donne la mesure et info les informations dessus.
    info est dictionnaire
    data est un array'''
    OrderKey = "id"
    def __init__(self, data, info, qualities = []):
        self.data = data
        self.info = info
        self.qualities = qualities
    def __str__(self):
        return self.data.__str__() + ", " + self.info.__str__()
    def __lt__(self, value):
        return self.info[Signal.OrderKey] < value.info[Signal.OrderKey]
    def __le__(self, value):
        return self.info[Signal.OrderKey] <= value.info[Signal.OrderKey]
        
        
        
class DatabaseManager:
    '''la spécification de la table principale qui permet de garder en memoire les mesures et détaillé dans createMesuresTable'''
    def __init__(self, fileDirectory, databaseFile):
        self._fileDirectory = fileDirectory
        self._databaseFile = databaseFile
        self.loadedSignal = dict()
        
    def saveSignal(self, sig):
        """ sauvegarde une mesure et l'insère dans la base de donnée. Pas besoin de renseigner 
        la date, la longueur et le nombre d'électrodes"""
        if(not "categorie" in sig.info):
            raise UndocumentedSignalError("categorie")
        if(not "protocole" in sig.info):
            raise UndocumentedSignalError("protocole")
        if(not "sujet" in sig.info):
            raise UndocumentedSignalError("sujet")
        if(not "session" in sig.info):
            raise UndocumentedSignalError("session")
        
        sig.info["date"] = datetime.now()
        sig.info["duree"] = sig.data[0,-1] - sig.data[0,0]
        sig.info["nb_electrodes"] = sig.data.shape[1]
        try:
            db = sqlite3.connect(self._databaseFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            curs = db.cursor()
            curs.execute("""INSERT INTO mesures(categorie, protocole, date, sujet, session, duree, nb_electrodes) 
                                        VALUES(:categorie, :protocole, :date, :sujet, :session, :duree, :nb_electrodes) """, sig.info)
            i = str(curs.lastrowid)
            DatabaseManager.writeFile(self._fileDirectory + i + ".eeg", sig.data)
            if len(sig.qualities):
                DatabaseManager.writeFile(self._fileDirectory + i + ".qua", sig.qualities[0])
            db.commit()
        except:
            print("error")
            print(sys.exc_info())
            db.rollback()
        db.close()
        
    def load(self, request):
        try:
            db = sqlite3.connect(self._databaseFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            curs = db.cursor()
            curs.execute(request)
            for sigs in curs.fetchall():
                self.loadedSignal[sigs[0]] = Signal(DatabaseManager.readFile(self._fileDirectory + str(sigs[0]) + ".eeg"),
                                                    dict([("id", sigs[0]), 
                                                          ("categorie", sigs[1]),
                                                          ("protocole", sigs[2]),
                                                          ("date", sigs[3]),
                                                          ("sujet", sigs[4]),
                                                          ("session", sigs[5]),
                                                          ("duree", sigs[6]),
                                                          ("nb_electrodes", sigs[7])
                                                          ]))
                try:
                    with open(self._fileDirectory + str(sigs[0]) + ".qua", 'r'):
                        pass
                    self.loadedSignal[sigs[0]].qualities = [DatabaseManager.readFile(self._fileDirectory + str(sigs[0]) + ".qua")]
                except:
                    self.loadedSignal[sigs[0]].qualities = []
        finally:
            db.rollback()
        db.close()
    def createMesureTable(self):
        db = sqlite3.connect(self._databaseFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curs = db.cursor()
        curs.execute("""CREATE TABLE IF NOT EXISTS mesures(
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                categorie TEXT,
                protocole TEXT,
                date Datetime,
                sujet TEXT,
                session INTEGRER,
                duree REAL,
                nb_electrodes INTEGER)""")
        db.commit()
        db.close()
    
    def createProtocoleTable(self):
        db = sqlite3.connect(self._databaseFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curs = db.cursor()
        curs.execute("""CREATE TABLE IF NOT EXISTS protocoles(
                protocole TEXT,
                date Datetime,
                tempsRepos REAL,
                nb_electrodes INTEGER)""")
        db.commit()
        db.close()
        
    def createPlacementTable(self):
        db = sqlite3.connect(self._databaseFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curs = db.cursor()
        curs.execute("""CREATE TABLE IF NOT EXISTS placements(
                protocole TEXT,
                electrode INTEGER,
                place TEXT)""")
        db.commit()
        db.close()
    
    def createExperienceTable(self):
        db = sqlite3.connect(self._databaseFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curs = db.cursor()
        curs.execute("""CREATE TABLE IF NOT EXISTS experience(
                protocole TEXT,
                categorie TEXT,
                temps INTEGER)""")
        db.commit()
        db.close()
    
    def saveProtocole(self, protocole):
        db = sqlite3.connect(self._databaseFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        try:
            curs = db.cursor()
            curs.execute(""" SELECT protocole FROM protocoles """)
            for sigs in curs.fetchall():
                if sigs[0] == protocole.num:
                    return
            sig = {"protocole" : protocole.num, "date" : datetime.now(), "tempsRepos" : protocole.tempsRepos, 
                   "nb_electrodes" : len(protocole.electrodes)}
            curs.execute("""INSERT INTO protocoles(protocole, date, tempsRepos, nb_electrodes) 
                                            VALUES(:protocole, :date, :tempsRepos, :nb_electrodes) """, sig)
            for i in range(len(protocole.electrodes)):
                sig = {"protocole" : protocole.num, "electrode" : i, "place" : protocole.electrodes[i]}
                curs.execute("""INSERT INTO placements(protocole, electrode, place) 
                                            VALUES(:protocole, :electrode, :place) """, sig)
            for xp in protocole.expe:
                sig = {"protocole" : protocole.num, "categorie" : xp.getCategorie(), "temps" : xp.getTime()}
                curs.execute("""INSERT INTO experience(protocole, categorie, temps) 
                                            VALUES(:protocole, :categorie, :temps) """, sig)
            db.commit()
        except:
            db.rollback()
            print("errure base de données")
            print(sys.exc_info())
        db.close()
    
    def readFile(file):
        lines = []
        with open(file, 'r') as f:
            s = f.read(1)
            line = []
            num = ""
            while s != "":
                while s != "\n" and s != "":
                    while s != "," and s != "":
                        num += s
                        s = f.read(1)
                    line.append(float(num))
                    num = ""
                    s = f.read(1)
                lines.append(line)
                line = []
                s = f.read(1)
        return array(lines)
                        
    def writeFile(file, data):
        with open(file, 'x') as f:
            for line in data:
                for num in line:
                    f.write(str(num) + ",")
                f.write("\n")

    def loadProtocoles(self):
        prots = []
        db = sqlite3.connect(self._databaseFile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curs = db.cursor()
        curs.execute(""" SELECT * FROM protocoles """)
        for sig in curs.fetchall():
            prot = protocole()
            prot.num = sig[0]
            prot.tempsRepos = sig[2]
            prot.electrodes = [0 for i in range(sig[3])]
            prot.expe = []
            #electrodes
            curs2 = db.cursor()
            curs2.execute("""SELECT electrode, place FROM placements WHERE protocole = """ + "\"" + prot.num + "\"")
            for ele in curs2.fetchall():
                prot.electrodes[ele[0]] = ele[1]
            curs2.execute("""SELECT categorie,temps FROM experience WHERE protocole = """ + "\"" + prot.num + "\"")
            for xp in curs2.fetchall():
                e = Experience('', xp[1])
                e.categorie = xp[0]
                prot.expe.append(e)
            prots.append(prot)
        return prots
                
    def absorb(self, db):
        prots = db.loadProtocoles()
        for p in prots:
            self.saveProtocole(p)
        db.load("""SELECT * FROM mesures""")
        for s in db.loadedSignal.values():
            self.saveSignal(s)



































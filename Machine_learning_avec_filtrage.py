#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 17:44:19 2019

@author: ahmed 

Two class (that only differ by the pre filtering applied to raw data) that we used as our machine learning engine
They can accept different classifying methods ('lda', 'knn', 'svm') and feature forms ('carte' or 'fft')
"""


import numpy as np
import random
from databaseManager import DatabaseManager
import matplotlib.pyplot as plt

from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn import svm

import carte as crt


def trainingdata(X,Y):#fabrique les vecteurs
    n=len(X)
    l=[j for j in range(n)]
    random.shuffle(l)
    
    X_train = np.array( [X[l[i]] for i in range(3*n//4)])
    X_test = np.array( [X[l[i]] for i in range(3*n//4, n)])
    
    Y_train = np.array([Y[l[i]] for i in range(int(3*n//4))])
    Y_test = np.array([Y[l[i]] for i in range(int(3*n//4),n)])
    return X_train, Y_train, X_test, Y_test

def fft(X,j):#transforme X en un vecteur d'arrays fourialisés
    freq = np.fft.rfftfreq(len(X[0]), 1./500.)
    fmin = 0
    fmax = 0
    for i in freq:
        if i > 5:
            break
        fmin += 1
    for i in freq:
        fmax += 1
        if i > 40:
            break
    
    X2 = [0 for i in range(len(X))]
    for i in range(len(X)):
        b=abs(np.fft.fft(X[i], norm = 'ortho')[:,fmin:fmax])
        X2[i]=b[j,:].flatten()
    return X2

def fftTot(X):
    X2 = [0 for i in range(len(X))]
    for i in range(len(X)):
        b=abs(np.fft.fft(X[i][1:9,:], norm = 'ortho'))
        X2[i]= b.flatten()
    return X2

def cartes(X):
    plt.ioff()#pour ne pas que les cartes s'affichent
    X2 = [0 for i in range(len(X))]
    for i in range(len(X)):
        #X2[i] = crt.getCarte(X[i], 30, 0.5, 5, 40)
        X2[i] = np.array([crt.spectoArray(X[i][j,:], 0, 40) for j in range(1,9) ]).flatten()
    plt.ion()
    return X2
    
def cartesE(X, j):
    X2 = [0 for i in range(len(X))]
    for i in range(len(X)):
        X2[i] = crt.getCarteElec(X[i], 10, 1, 5, 40, j)
    return X2


###K plus proches voisins
def PlusProcheVoisin(X_train, Y_train,X_test, Y_test):
    # on charge le modele KNN
    knn = KNeighborsClassifier(n_neighbors = 5) # on est contraints à choisir un petit nombre car nous n'avons pas beaucoup d'échantillons
    # On entraine le modele pour fit le mieux nos data
    knn.fit(X_train,Y_train)
    Y_prediction_knn=knn.predict(X_test)
    
    n = 0
    for i in Y_prediction_knn - Y_test:
        if i == 0:
            n+=1
    return n/len(Y_test)
        
###Modele LDA ( Linear discriminant analysis ( suggeré par l'une des theses de la biblio) inference bayesienne. Censé etre efficace avec des gros vecteurs!
def LDA(X_train, Y_train, X_test, Y_test):
    lda=LinearDiscriminantAnalysis()
    lda.fit(X_train,Y_train)
    Y_prediction_lda=lda.predict(X_test)
   
    n = 0
    for i in Y_prediction_lda - Y_test:
        if i == 0:
            n+=1
    return n/len(Y_test)
    
def initialize_ml(protocole="'2.0.0'",N=50, clas =  'lda'):# retourne tous les objets utiles , les range dans 2 listes :ml_fft et ml_cartes
    db=DatabaseManager("data/enregistrements/","data/table.db")
    s="SELECT * FROM mesures WHERE (categorie = 'calcul mental' OR categorie = 'mouvement imaginé' ) AND protocole = "
    s += protocole
    db.load(s)
    ml=Machine_learning_avec_filtrage(db, 10, 100)
    ml_fft = 0
    print(str(len((db.loadedSignal).keys())) + " signal loaded in the database")
    ml.treat('fft', 0)
    print("fft treated")
    for _ in range(N):
        ml.train(clas)
        ml_fft +=ml.score()/N
    print(" fft : " + str(ml_fft))
    ml.treat('carte', 0)
    print("catre treated")
    ml_carte = 0
    for _ in range(N):
            ml.train(clas)
            ml_carte+=ml.score()/N
    return(ml_fft,ml_carte)

def test_ml(db,N=100, clas =  'lda'):
    print(str(len((db.loadedSignal).keys())) + " signal loaded in the database")
    ml=Machine_learning_avec_filtrage(db, 10, 100)
    print("filtered")
    ml.treat('carte', 0)
    print("catre treated")
    ml_carte = 0
    for i in range(N):
        if i%20 == 0:
            print(i)
        ml.train(clas)
        ml_carte+=ml.score()/N
    return ml_carte

        
class Machine_learning_sans_filtrage : #db a deja les signaux loadés
    def __init__(self,db,nbr_features=990):
        self.nbr_features=nbr_features
        self.X = []
        self.Y = []
        self.X1=[]
        l = (db.loadedSignal).keys() 
        for i in l:
            string=db.loadedSignal[i].info["categorie"]
            if string=="calcul mental":
                self.Y.append(0)
                self.X.append(db.loadedSignal[i].data[:,:990])#1000=2 sec
         
            if string=="mouvement imaginé" :
                (self.Y).append(1)
                (self.X).append(db.loadedSignal[i].data[:,:990])   
        
        #on a rempli les vecteurs. Plus qu'a entrainer le classifier.
        
    def treat(self,cat,electrode):
        self.cat = cat
        self.electrode = electrode
        if cat=="fft":
            if electrode==0:
                self.X1=fftTot(self.X)
            else:
                self.X1=fft(self.X,electrode)
        elif cat=="carte":
            if electrode==0:
                self.X1=cartes(self.X)
            else:
                self.X1=cartesE(self.X,electrode)
        elif cat=='no':
            self.X1 = [a.flatten() for a in self.X]
                
    def train(self, type_classifier): 
        self.type_classifier=type_classifier
        self.X_train,self.Y_train,self.X_test,self.Y_test=trainingdata(self.X1,self.Y)#classifier='knn' or 'lda' or ...
        
        if type_classifier=='knn':
            # on charge le modele KNN
            self.classifier = KNeighborsClassifier(n_neighbors = 5) # on est contraints à choisir un petit nombre car nous n'avons pas beaucoup d'échantillons
            # On entraine le modele pour fit le mieux nos data
            (self.classifier).fit(self.X_train,self.Y_train)
        if type_classifier=='lda':
            self.classifier=LinearDiscriminantAnalysis() 
            (self.classifier).fit(self.X_train,self.Y_train)
        if type_classifier == 'svm':
            self.classifier = svm.NuSVC(gamma='scale')
            self.classifier.fit(self.X_train, self.Y_train)
    
    def train_interface(self,type_classifier):
        self.type_classifier=type_classifier
        if type_classifier=='knn':
            # on charge le modele KNN
            self.classifier = KNeighborsClassifier(n_neighbors = 5) # on est contraints à choisir un petit nombre car nous n'avons pas beaucoup d'échantillons
            # On entraine le modele pour fit le mieux nos data
            self.classifier.fit(self.X1,self.Y)
        if type_classifier=='lda':
            self.classifier=LinearDiscriminantAnalysis() 
            self.classifier.fit(self.X1,self.Y)
            
    def predict(self, X1):#probas,
        X1 = X1[:, :self.nbr_features]
        if self.cat=="fft":
           if self.electrode==0:
               X1=fftTot([X1])
           else:
                X1=fft([X1],self.electrode)
        else:
            if self.electrode==0:
                X1=cartes([X1])
            else:
                X1=cartesE([X1],self.electrode)
        if self.type_classifier=='lda':
            return self.classifier.predict_proba(X1)[0][0]
        if self.type_classifier=='knn':
            return self.classifier.predict_proba(X1)[0][0]
       
    def score(self):
        if self.type_classifier=='lda':
            return self.classifier.score(self.X_test,self.Y_test)
        if self.type_classifier=='knn':
            return self.classifier.score(self.X_test,self.Y_test)
        if self.type_classifier == 'svm':
            return self.classifier.score(self.X_test, self.Y_test)

class Machine_learning_avec_filtrage(Machine_learning_sans_filtrage):
    def __init__(self,db,fenetreMoy = 10, fenetreLine = 100, nbr_features=990):
        Machine_learning_sans_filtrage.__init__(self, db, nbr_features)
        self.fenetreLine = fenetreLine
        self.fenetreMoy = fenetreMoy
        for i in range(len(self.X)):#etape de filtrage
            self.X[i] = crt.filtreSignal(self.X[i], fenetreLine=fenetreLine, fenetreMoy=fenetreMoy)
    
    
    def test_filtrage(self,type_classifier,cat,N):
        l=[0 for j in range(9)]
        for j in range(N):
            for i in range(9):
                self.train(type_classifier,cat,i)
                l[i]+=self.score()/N
        return(l)
    def predict(self,X1):
        X1 = X1[:, :self.nbr_features]
        X1 = crt.filtreSignal(X1, fenetreLine=self.fenetreLine, fenetreMoy=self.fenetreMoy)
        if self.cat=="fft":
           if self.electrode==0:
               X1=fftTot([X1])
           else:
                X1=fft([X1],self.electrode)
        else:
            if self.electrode==0:
                X1=cartes([X1])
            else:
                X1=cartesE([X1],self.electrode)
        if self.type_classifier=='lda':
            return self.classifier.predict_proba(X1)[0][0]
        elif self.type_classifier=='knn':
            return self.classifier.predict_proba(X1)[0][0]
            
        
        
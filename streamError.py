# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 13:06:26 2018

@author: Alexis

Errors for streamListener
"""

class UnConnctedStreamError(Exception):
    def __init__(self, action):
        self.action = action
    def __str__(self):
        return "tentative de " + self.action + " sur un StreamListener non connecté"
    
class RecordingSreamError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "retrait du buffer sur un stream en train d' enregistrer"
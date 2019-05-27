# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 18:42:59 2019

@author: Alexis

This file just contains a basic class to communicate with a arduino controlled arm
"""


from serial import Serial

class Arduino:
    def __init__(self, port):
        self.usb = Serial(port=port, baudrate='9600')
        
    def sendInt(self, i):
        self.usb.write(bytes([i]))
        
        
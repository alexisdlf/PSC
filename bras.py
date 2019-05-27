# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 18:05:51 2019

@author: Alexis
"""

import tkinter as tk
from math import sin, cos
import random

class Bras(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master, height = 420, width = 1000, background = 'white')    
        self.epaule_r = 30
        self.epaule_o = -0.2
        self.epaule_x = 500
        self.epaule_y = 200
       
        self.bras_l = 200
        self.coude_r = 25
        self.coude_o = 45/180*3.141
        self.coude_x = 250
        self.coude_y = 300
        
        self.abras_h = 15
        self.abras_l = 180
        self.poignee_r = 20
        self.poignee_x = 430
        self.poignee_y = 300
       
        self.selectedArt = 0
        self.attrap = 0
        self.increment = 0.01
        
        self.epaule = self.create_line(0,0,0,0)
        self.bras = self.create_line(0,0,0,0)
        self.coude = self.create_line(0,0,0,0)
        self.abras = self.create_line(0,0,0,0)
        
        self.poignee = self.create_line(0,0,0,0)
       
        self.info = ""
        self.text = self.create_text(5, 5, text=self.info)
        
        self.obj_r = 5
        self.obj_x = 0
        self.obj_y = 0
        self.obj_o = 0
        self.obj = self.create_line(0,0,0,0)
        self.coude_x = self.epaule_x + self.bras_l*cos(self.epaule_o)
        self.coude_y = self.epaule_y - self.bras_l*sin(self.epaule_o)
        self.putObj()

        
    def draw(self):
        self.delete(self.text)
        self.text = self.create_text(5, 5, text=self.info, anchor = 'nw', font = ('Helvetica', '16'))
        self.drawEpaule()
        self.drawObj()
        
    def drawEpaule(self):
        color = 'white'
        if self.selectedArt == 0:
            color = 'red'
        self.delete(self.epaule)
        self.drawBras()
        self.epaule = self.create_oval(self.epaule_x - self.epaule_r, self.epaule_y - self.epaule_r, 
                                       self.epaule_x + self.epaule_r, self.epaule_y + self.epaule_r,
                                       width = 1, outline = 'black', fill = color)
        
    def drawBras(self):
        self.delete(self.bras)
        self.coude_x = self.epaule_x + self.bras_l*cos(self.epaule_o)
        self.coude_y = self.epaule_y - self.bras_l*sin(self.epaule_o)
        x = [(self.epaule_x - self.epaule_r*sin(self.epaule_o), self.epaule_y - self.epaule_r*cos(self.epaule_o)),
             (self.epaule_x + self.epaule_r*sin(self.epaule_o), self.epaule_y + self.epaule_r*cos(self.epaule_o)),
             (self.coude_x + self.coude_r*sin(self.epaule_o), self.coude_y + self.coude_r*cos(self.epaule_o)),
             (self.coude_x - self.coude_r*sin(self.epaule_o), self.coude_y - self.coude_r*cos(self.epaule_o))]
        self.bras = self.create_polygon(x, fill = 'grey', width = 1, outline = 'black')
        self.drawCoude()
        
    def drawCoude(self):
        color = 'white'
        if self.selectedArt == 1:
            color = 'red'
        self.delete(self.coude)
        self.drawABras()
        self.coude = self.create_oval(self.coude_x - self.coude_r, self.coude_y - self.coude_r,
                                      self.coude_x + self.coude_r, self.coude_y + self.coude_r,
                                      width = 1, outline = 'black', fill = color)
        
        
    def drawABras(self):
        self.delete(self.abras)
        self.poignee_x = self.coude_x + self.abras_l*cos(self.coude_o + self.epaule_o)
        self.poignee_y = self.coude_y - self.abras_l*sin(self.coude_o + self.epaule_o)
        x = [(self.coude_x - self.coude_r*sin(self.coude_o + self.epaule_o), self.coude_y - self.coude_r*cos(self.coude_o + self.epaule_o)),
             (self.coude_x + self.coude_r*sin(self.coude_o + self.epaule_o), self.coude_y + self.coude_r*cos(self.coude_o + self.epaule_o)),
             (self.poignee_x + self.poignee_r*sin(self.coude_o + self.epaule_o), self.poignee_y + self.poignee_r*cos(self.coude_o + self.epaule_o)),
             (self.poignee_x - self.poignee_r*sin(self.coude_o + self.epaule_o), self.poignee_y - self.poignee_r*cos(self.coude_o + self.epaule_o))]
        self.abras = self.create_polygon(x, fill = 'grey', width = 1, outline = 'black')
        self.drawPoignee()
        
    def drawPoignee(self):
        color = 'white'
        if self.attrap == 1:
            color = 'yellow'
        self.delete(self.poignee)
        self.poignee = self.create_oval(self.poignee_x - self.poignee_r, self.poignee_y - self.poignee_r,
                                       self.poignee_x + self.poignee_r, self.poignee_y + self.poignee_r,
                                       width = 1, fill = color, outline = 'black')
    
    def attraper(self):
        self.attrap = 1
        if (self.poignee_x - self.obj_x)**2 + (self.poignee_y - self.obj_y)**2 < (self.poignee_r + self.obj_r)**2:
            self.putObj()
            print("touché !")
        else:
            print("dommage !")
    
    def ouvrir(self):
        self.attrap = 0
        
        
    def nextArt(self):
        self.selectedArt += 1
        self.selectedArt %= 2
        
    def move(self):
        if self.selectedArt == 0:
            self.epaule_o += self.increment
        if self.selectedArt == 1:
            self.coude_o += self.increment
        
    def putObj(self):
        self.obj_o = random.random()*3.14
        self.obj_x = self.coude_x + self.abras_l*cos(self.obj_o)# + random.randint(-2, 2)
        self.obj_y = self.coude_y - self.abras_l*sin(self.obj_o)# + random.randint(-2, 2)
        
    def drawObj(self):
        self.delete(self.obj)
        self.obj = self.create_oval(self.obj_x - self.obj_r, self.obj_y - self.obj_r, 
                                    self.obj_x + self.obj_r, self.obj_y + self.obj_r,
                                    width = 1, outline = 'black', fill = 'green')  
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
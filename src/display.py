'''
    File name: display.py
    Author: Isaiah Johnson
    Date created: 3/30/2020
    Python Version: 3.8
'''

import tkinter

class Display:

    def __init__(self):
        self.pixels = []
        self.window = tkinter.Tk()
        self.scale = 8
        self.width = 64*self.scale
        self.height = 32*self.scale
        self.foregroundColor = '#000'
        self.backgroundColor = '#fff'
        self.window.geometry = ("%dx%d"%(self.width,self.height))
        self.window.config(bg=self.backgroundColor)
        self.canvas = tkinter.Canvas(self.window, bg=self.backgroundColor, height = self.height, width = self.width)
        self.canvas.pack()
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append([self.canvas.create_rectangle(x*self.scale,y*self.scale,(x+1)*self.scale,(y+1)*self.scale), 0])
            self.pixels.append(row)

    def setTitle(self, title):
        self.window.title(title)
    def clear(self):
        for pixel in self.pixels:
            self.canvas.delete(pixel[0])

    def set(self, row, col, value):
        pixel = self.pixels[row][col]
        if(value == 0):
            pixel[1] = 0
            self.canvas.itemconfig(pixel[0], fill=self.backgroundColor)
        else:
            self.canvas.itemconfig(pixel[0], fill=self.foregroundColor)
            self.pixels[row][col][1] = 1

    def get(self, row, col):
        return self.pixels[row][col][1]

    def update(self):
        self.window.update()

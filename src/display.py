'''
    File name: display.py
    Author: Isaiah Johnson
    Date created: 3/30/2020
    Python Version: 3.8
'''

import tkinter

class Display:

    def __init__(self):
        self.__pixels = []
        self.__window = tkinter.Tk()
        self.__scale = 16
        self.__width = 64*self.__scale
        self.__height = 32*self.__scale
        self.__foregroundColor = '#183A37'
        self.__backgroundColor = '#04151F'
        self.__window.geometry = ("%dx%d"%(self.__width,self.__height))
        self.__window.config(bg=self.__backgroundColor)
        self.__canvas = tkinter.Canvas(self.__window, bg=self.__backgroundColor, height = self.__height, width = self.__width)
        self.__canvas.pack()
        for y in range(self.__height):
            row = []
            for x in range(self.__width):
                row.append([self.__canvas.create_rectangle(x*self.__scale,y*self.__scale,(x+1)*self.__scale,(y+1)*self.__scale, width=1, outline='#0f2422'), 0])
            self.__pixels.append(row)
    def setTitle(self, title):
        self.__window.title(title)
    def clear(self):
        for pixel in self.__pixels:
            self.__canvas.delete(pixel[0])

    def set(self, row, col, value):
        pixel = self.__pixels[row][col]
        if(value == 0):
            pixel[1] = 0
            self.__canvas.itemconfig(pixel[0], fill=self.__backgroundColor)
        else:
            self.__canvas.itemconfig(pixel[0], fill=self.__foregroundColor)
            self.__pixels[row][col][1] = 1

    def get(self, row, col):
        return self.__pixels[row][col][1]

    def update(self):
        self.__window.update()

'''
    File name: chip8Emulator.py
    Author: Isaiah Johnson
    Date created: 3/23/2020
    Python Version: 3.8
'''

import tkinter
import time
import math
import processor
import display
import rom

class Chip8Emulator:

    def __init__(self):
        self.__title = "Chip-8 Emulator"
        self.__display = display.Display()
        self.__keyboard == keyboard.Keyboard()
        self.__processor = processor.Processor(self.__display, self.__keyboard)
        self.__isRunning = False
        self.__debugMode = True
        self.__display.setTitle(self.__title)

    def run(self, rom):
        self.__processor.loadROM(rom)
        self.__isRunning = True
        step = 0
        while(self.__isRunning):
            if(self.__debugMode and step == 0):
                skip = input("Step#:")
                if(skip.isnumeric()):
                    step = int(skip)
                else:
                    step = 0
            else:
                time.sleep(self.__processor.getClockSpeed())
            self.__processor.emulateCycle()
            step -= 1
            if(step < 0):
                step = 0

emulator = Chip8Emulator()
emulator.run(rom.test2)

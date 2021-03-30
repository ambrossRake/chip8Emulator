'''
    File name: chip8Emulator.py
    Author: Isaiah Johnson
    Date created: 3/23/2020
    Python Version: 3.8
'''

import tkinter
import time
import math
from processor import *
from display import *
from rom import *

class Chip8Emulator:

    def __init__(self):
        self.title = "Chip-8 Emulator"
        self.display = Display()
        self.processor = Processor(self.display)
        self.isRunning = False
        self.debugMode = True
        self.display.setTitle(self.title)

    def run(self, rom):
        self.processor.loadROM(rom)
        self.isRunning = True
        step = 0
        while(self.isRunning):
            if(self.debugMode and step == 0):
                skip = input("Step#:")
                if(skip.isnumeric()):
                    step = int(skip)
                else:
                    step = 0
            else:
                time.sleep(self.processor.clockSpeed)
            self.processor.emulateCycle()
            step -= 1
            if(step < 0):
                step = 0

emulator = Chip8Emulator()
emulator.run(test2)

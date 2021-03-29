'''
    File name: Chip8Emulator.py
    Author: Isaiah Johnson
    Date created: 3/23/2020
    Python Version: 3.8
'''

import tkinter
import time
import math
import logging as log
from rom import *

log.basicConfig(filename='test.log', level=log.INFO)

logger = log.getLogger()
handler = log.StreamHandler()
handler.setLevel(log.INFO)
formatter = log.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

handler = log.FileHandler("debug.log","w", encoding=None, delay="true")
handler.setLevel(log.DEBUG)
formatter = log.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

handler = log.FileHandler("error.log","w", encoding=None, delay="true")
handler.setLevel(log.ERROR)
formatter = log.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Chip8Emulator:

    def __init__(self):
        self.memory = []
        self.v = []
        self.i = 0x0
        self.pc = 0x200
        self.stack = []
        self.sp = 0x0
        self.opCode = 0x0
        self.isRunning = True
        self.clockSpeed = .2
        self.debugMode = True
        self.pixels = []
        self.dT = 0x0
        self.window = tkinter.Tk()
        self.graphicScale = 8
        self.displayWidth = 64*self.graphicScale
        self.displayHeight = 32*self.graphicScale
        self.font = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80]  # F

        self.window.title("Chip8 Emulator")
        self.window.geometry = ("%dx%d"%(self.displayWidth,self.displayHeight))
        self.window.config(bg='#000')
        self.canvas = tkinter.Canvas(self.window, bg="#000", height = self.displayHeight, width = self.displayWidth)
        self.canvas.pack()
        for _ in range(4096):
            self.memory.append(0x0)
        for _ in range(16):
            self.v.append(0x0)
        for i in range(len(self.font)):
            self.memory[0x050+i] = self.font[i]

        for y in range(self.displayHeight):
            row = []
            for x in range(self.displayWidth):
                row.append([self.canvas.create_rectangle(x*self.graphicScale,y*self.graphicScale,(x+1)*self.graphicScale,(y+1)*self.graphicScale), 0])
            logger.info("Loading pixels [%d/%d]"%(self.displayWidth*y, self.displayWidth*self.displayHeight))
            self.pixels.append(row)

    def loadROM(self, rom):
        for i in range(len(rom)):
            self.memory[self.pc+i] = rom[i]

    def emulateCycle(self):
        opCodeA = self.memory[self.pc]
        opCodeB = self.memory[self.pc+1]
        self.opCode = int(opCodeA) << 8 | int(opCodeB)

        opA = self.opCode & 0xF000
        opB = (self.opCode & 0x0F00) >> 8
        opC = (self.opCode & 0x00F0) >> 4
        opD = self.opCode & 0x000F
        if(opA == 0x0000):
            if(self.opCode & 0x00FF == 0x00EE):
                self.ret()
            elif(opC == 0xE):
                self.clr()
        elif(opA == 0x1000):
            self.jmp(self.opCode & 0x0FFF)
        elif(opA == 0x2000):
            self.call(self.opCode & 0x0FFF)
        elif(opA == 0x3000):
            self.sex(opB, self.opCode&0x00FF)
        elif(opA == 0x4000):
            self.sne(opB, self.opCode&0x00FF)
        elif(opA == 0x5000):
            self.se(opB, opC)
        elif(opA == 0x6000):
            self.movL(opB, self.opCode&0x00FF)
        elif(opA == 0x7000):
            self.add(opB, self.opCode & 0x00FF)
        elif(opA == 0x8000):
            if(opD == 0x0000):
                self.ldxy(opB, opC)
            elif(opD == 0x0001):
                self.orx(opB, opC)
            elif(opD == 0x0002):
                self.andx(opB, opC)
            elif(opD == 0x0005):
                self.sub(opB, opC)
            elif(opD == 0x0007):
                self.subn(opB, opC)
        elif(opA == 0x9000):
            self.snel(opB, opC)
        elif(opA == 0xA000):
            self.loadI(self.opCode&0x0FFF)
        elif(opA == 0xD000):
            self.sprite(opB, opC, opD)
        elif(opA == 0xF000):
            opCD = self.opCode & 0x00FF
            if(opCD == 0x0007):
                self.loadXDT(opB)
            if(opCD == 0x0015):
                self.loadDT(opB)

            if(opCD == 0x0029):
                self.loadFX(opB)
            elif(opCD == 0x0033):
                self.bcd(opB)
            elif(opCD == 0x0065):
                self.loadXI(opB)

        else:
            self.isRunning = False
            logger.error("OpCode implementation for %s not found"%(hex(self.opCode)))


        logger.info(self.toString())
        self.pc += 2
        self.window.update()

    def ldxy(self, x, y):
        logger.info("Loading value from v[%d] into v[%d]"%(y, x))
        self.v[x] = self.v[y]

    def andx(self, x, y):
        logger.info("v[%d] = v[%d] & v[%d]"%(x,x,y))
        self.v[x] = self.v[x] & self.v[y]

    def orx(self, x, y):
        logger.info("v[%d] = v[%d] | v[%d]"%(x,x,y))
        self.v[x] = self.v[x] | self.v[y]

    def subn(self, x, y):
        if(self.v[y] > self.v[x]):
            self.v[y] -= self.v[x]
            self.v[0xF] = 1
        else:
            self.v[0xF] = 0

    def sub(self, x,y):
        if(self.v[x] > self.v[y]):
            logger.info("Subtracting " + str(self.v[y]) + " from " + str(self.v[x]))
            self.v[x] -= self.v[y]
            self.v[0xF] = 1
        else:
            self.v[0xF] = 0

    def sne(self, v, x):
        if(self.v[v] != x):
            logger.info("Skipping next instruction")
            self.pc += 2
        else:
            logger.info("Ignoring skip")

    def se(self, x, y):
        if(self.v[x] == self.v[y]):
            logger.info("Skipping next instruction")
            self.pc += 2
        else:
            logger.info("Ignoring skip")

    def loadXDT(self, v):
        logger.info("Placing delay timer value into register v[" + str(v) + "]")
        self.v[v] = self.dT

    def loadDT(self, v):
        logger.info("Setting delay timer to " + str(v))
        self.dT = self.v[v]

    def loadFX(self, v):
        logger.info("Setting vI to the address of sprite #" + str(self.v[v]))
        self.i = 0x50 + (self.v[v] * 5)

    def loadXI(self, v):
        for i in range(0,v):
            logger.info("Loading value " + str(int(self.memory[self.i+i])) + " into register v" + str(i))
            self.v[i] = int(self.memory[self.i+i])

    def jmp(self, x):
        logger.info("Jumping to address: " + str(x))
        self.pc = x

    def sex(self, v, x):
        if(self.v[v] == x):
            logger.info("Skipping next instruction")
            self.pc += 2
        else:
            logger.info("Ignoring Skip")

    def ret(self):
        logger.info("Returning from sub routine")
        self.pc = self.stack.pop()
        self.sp -= 1

    def add(self, v, x):
        logger.info("Adding " + str(x) + " to register v["+ str(v) + "]" )
        self.v[v] += x

    def bcd(self, v):
        value = self.v[v]
        logger.info("Storing value " + str(value) + " into memory locations{\n" + str(hex(self.i)) + ", " + str(hex(self.i+1)) + ", " + str(hex(self.i+2)))
        ones = value % 10
        tens = (value / 10) % 102
        hundreds = value / 100
        self.memory[self.i] = hundreds
        self.memory[self.i+1] = tens
        self.memory[self.i+2] = ones

    def call(self,n):
        logger.info("Calling subroutine at address " + str(hex(n)))
        self.sp += 1
        self.stack.append(self.pc)
        self.pc = n

    def spriteCheck(self, x,y):
        logger.info(self.pixels[y][x])
        return(self.pixels[y][x][1])
    def clr(self):
        for pixel in self.pixels:
            canvas.delete(pixel[0])

    def sprite(self, x, y, n):
        x-=7
        x*=4
        y-=8
        y*=2

        if(x>63):
            x=math.floor(x/63)
        logger.info("Drawing sprite at %d, %d with a height of %d"%(x,y,n))
        for byte_i in range(n):
            byte = [int(x) for x in '{:08b}'.format(self.memory[self.i+byte_i])]
            logger.debug("Reading byte #" + str(byte_i) + ":")
            logger.debug(byte)
            for bit_i in range(len(byte)):
                bit = byte[bit_i]
                logger.debug("Bit: " + str(bit))
                pixel = self.pixels[y+byte_i][x+bit_i]
                if(bit ^ pixel[1]):
                    logger.debug("Drawing Rectangle")
                    logger.debug("y*self.graphicScale*byte_i = %d*%d*%d"%(y,self.graphicScale,byte_i))
                    logger.debug("x*self.graphicScale*(bit_i+1) = %d%d,%d"%(x,self.graphicScale,bit_i))
                    #pixel = canvas.create_rectangle((x*self.graphicScale)+(bit_i*self.graphicScale), (y*self.graphicScale)+(byte_i*self.graphicScale),((x+1)*self.graphicScale)+(bit_i*self.graphicScale), ((y+1)*self.graphicScale)+(byte_i*self.graphicScale), fill='white')
                    self.canvas.itemconfig(pixel[0], fill='white')
                    pixel[1] = 1
                    #pixel = canvas.create_rectangle((x*self.graphicScale)+(bit_i*self.graphicScale), (y*self.graphicScale)+(byte_i*self.graphicScale),((x+1)*self.graphicScale)+(bit_i*self.graphicScale), ((y+1)*self.graphicScale)+(byte_i*self.graphicScale), fill='white')
                    #self.spriteData.append([pixel, x+bit_i, y+byte_i])
                    logger.debug("(%d,%d) -> (%d,%d)"%((x+1)*self.graphicScale*(bit_i+1), y*self.graphicScale*(byte_i+1),(x+1)*self.graphicScale*(bit_i+1), (y+1)*self.graphicScale*(byte_i+1)))
                else:
                    self.canvas.itemconfig(pixel[0], fill='black')
                    pixel[1] = 0
    def movL(self, v, x):
        logger.info("Moving constant " + str(x) + " into register v["+str(v)+"]")
        self.v[v] = x

    def loadI(self, x):
        logger.info("Loading constant " + str(x) + " into index register")
        self.i = x

    def snel(self, x, y):
        if(self.v[x] != self.v[y]):
            logger.info("Skipping next instruction")
            self.pc += 2
        else:
            logger.info("Skip ignored")


    def toString(self):
        out = "Emulator Info:\n"
        out += "Current OpCode:" + str(hex(self.opCode)) + "\n"
        out += "vR[" + str(self.i) + "]\n"
        for i in range(len(self.v)):
            out = out + "v" + str(i) + "[" + str(self.v[i]) + "]\t"

        out = out + "\n" + "Program Counter: " + str(self.pc) + "\n" + "Stack Pointer: " + str(self.sp) + "\n"
        return out

    def run(self):
        step = 0
        while(self.isRunning):
            if(self.debugMode and step == 0):
                skip = input("Step#:")
                if(skip.isnumeric()):
                    step = int(skip)
                else:
                    step = 0
            else:
                time.sleep(self.clockSpeed)
            self.emulateCycle()
            step -= 1
            if(step < 0):
                step = 0

emulator = Chip8Emulator()
emulator.loadROM(test2)
emulator.run()

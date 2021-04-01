'''
    File name: processor.py
    Author: Isaiah Johnson
    Date created: 3/30/2020
    Python Version: 3.8
'''

import tkinter
import time
import math
import logging as log

log.basicConfig(filename='../Emulator/log/test.log', level=log.DEBUG)

logger = log.getLogger()
handler = log.StreamHandler()
handler.setLevel(log.DEBUG)
formatter = log.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

handler = log.FileHandler("../Emulator/log/debug.log","w", encoding=None, delay="true")
handler.setLevel(log.DEBUG)
formatter = log.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

handler = log.FileHandler("../Emulator/log/error.log","w", encoding=None, delay="true")
handler.setLevel(log.ERROR)
formatter = log.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Processor:

    def __init__(self, display):
        self.memory = []
        self.v = []
        self.i = 0x0
        self.pc = 0x200
        self.stack = []
        self.sp = 0x0
        self.opCode = 0x0
        self.isRunning = True
        self.hertz = 500
        self.clockSpeed = 1/self.hertz
        self.debugMode = True
        self.pixels = []
        self.dT = 0x0
        self.sT = 0x0
        self.display = display
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

        for _ in range(4096):
            self.memory.append(0x0)
        for _ in range(16):
            self.v.append(0x0)
        for i in range(len(self.font)):
            self.memory[0x50+i] = self.font[i]

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
                logger.info("Returning from sub routine")
                self.ret()
            elif(opC == 0xE):
                logger.info("Clearing screen")
                self.clr()
        elif(opA == 0x1000):
            addr = self.opCode & 0x0FFF
            logger.info("Jumping to address: %s"%(hex(addr)))
            self.jmp(addr)
        elif(opA == 0x2000):
            addr = self.opCode & 0x0FFF
            logger.info("Calling subroutine at address %s"%(hex(addr)))
            self.call(addr)
        elif(opA == 0x3000):
            skipped = self.sex(opB, self.opCode&0x00FF)
            if(skipped):
                logger.info("Skipping next instruction")
            else:
                logger.info("Ignoring Skip")
        elif(opA == 0x4000):
            logger.info("Checking if %d != %d"%(opB,opC))
            skipped = self.sne(opB, self.opCode&0x00FF)
            if(skipped):
                logger.info("Skipping next instruction")
            else:
                logger.info("Ignoring skip")
        elif(opA == 0x5000):
            logger.info("Checking if %d == %d"%(opB,opC))
            skipped = self.se(opB, opC)
            if(skipped):
                logger.info("Skipping next instruction")
            else:
                logger.info("Ignoring skip")
        elif(opA == 0x6000):
            const = self.opCode&0x00FF
            logger.info("Moving constant %d into register v[%d]"%(const, opB))
            self.movL(opB, const)
        elif(opA == 0x7000):
            const = self.opCode&0x00FF
            logger.info("Adding constant %d to v[%d]"%(const, opB))
            self.add(opB, const)
        elif(opA == 0x8000):
            if(opD == 0x0000):
                logger.info("Loading value from v[%d] into v[%d]"%(opC, opB))
                self.ldxy(opB, opC)
            elif(opD == 0x0001):
                logger.info("v[%d] = v[%d] | v[%d]"%(x,x,y))
                self.orx(opB, opC)
            elif(opD == 0x0002):
                logger.info("v[%d] = v[%d] & v[%d]"%(x,x,y))
                self.andx(opB, opC)
            elif(opD == 0x0004):
                logger.info("Adding registers v[%d] and v[%d] into v[%]"%(opB, const, opB))
                self.addc(opB, opC)
            elif(opD == 0x0005):
                canSub = self.sub(opB, opC)
                if(canSub):
                    logger.info("Subtracting v[%d] from v[%d]"%(opC, opB))
            elif(opD == 0x0007):
                #TODO: Add log
                self.subn(opB, opC)

        elif(opA == 0x9000):
            skipped = self.snel(opB, opC)
            if(skipped):
                logger.info("Skipping next instruction")
            else:
                logger.info("Skip ignored")

        elif(opA == 0xA000):
            const = self.opCode&0x0FFF
            logger.info("Loading constant %d into index register"%(const))
            self.loadI(const)

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

        if((self.pc-0x200) % 60 == 0):
            if(self.dT > 0):
                self.dT -= 1
            if(self.sT > 0):
                logger.info("BEEP")
                self.sT -= 1

        self.display.update()

    def ldxy(self, x, y):
        self.v[x] = self.v[y]

    def andx(self, x, y):
        self.v[x] = self.v[x] & self.v[y]

    def orx(self, x, y):
        self.v[x] = self.v[x] | self.v[y]

    def subn(self, x, y):
        if(self.v[y] > self.v[x]):
            self.v[y] -= self.v[x]
            self.v[0xF] = 1
        else:
            self.v[0xF] = 0

    def sub(self, x,y):
        if(self.v[x] > self.v[y]):
            self.v[x] -= self.v[y]
            self.v[0xF] = 1
            return True
        else:
            self.v[0xF] = 0
            return False

    def add(self, v, const):
        sum = self.v[v]+const
        print("SUM: %d"%(sum))
        if(sum < 0xFF):
            self.v[v] = sum
        else:
            self.v[v] = sum & 0xFF 

    def addc(self, x, y):
        sum = self.v[x]+self.v[y]
        if(sum < 0xFF):
            self.v[x] = sum
        elif(sum > 0xFF):
            carry = 0xFF-(self.v[x]+self.v[y])
            if(carry >= 0xFF):
                self.v[0xF] = 0xFF
            else:
                self.v[0xF] = carry
            return carry
        else:
            self.v[x] = 0xFF

        return 0

    def sne(self, v, x):
        if(self.v[v] != x):
            self.pc += 2
            return True
        else:
            return False

    def se(self, x, y):
        if(self.v[x] == self.v[y]):
            self.pc += 2
            return True
        else:
            return False
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
        if(x < len(self.memory) and x > 0):
            self.pc = x

    def sex(self, v, x):
        if(self.v[v] == x):
            self.pc += 2
            return True
        else:
            return False

    def ret(self):
        self.pc = self.stack.pop()
        self.sp -= 1

    def bcd(self, v):
        value = self.v[v]
        logger.info("Storing value " + str(value) + " into memory locations{\n" + str(hex(self.i)) + ", " + str(hex(self.i+1)) + ", " + str(hex(self.i+2)))
        ones = value % 10
        tens = (value / 10) % 102
        hundreds = value / 100
        self.memory[self.i] = hundreds
        self.memory[self.i+1] = tens
        self.memory[self.i+2] = ones

    def call(self, addr):
        self.sp += 1
        self.stack.append(self.pc)
        self.pc = addr

    def clr(self):
        self.display.clear()

    def sprite(self, x, y, n):
        logger.info("Drawing sprite at %d, %d with a height of %d"%(self.v[x],self.v[y],n))

        for i in range(n):
            byte = [int(a) for a in '{:08b}'.format(self.memory[self.i+i])]
            logger.debug("Reading byte #" + str(i) + ":")
            logger.debug(byte)
            for j in range(len(byte)):
                bit = byte[j]
                logger.debug("Bit: " + str(bit))
                row = self.v[y]+i
                col = self.v[x]+j
                if(row > 32):
                    row %= 32
                if(col > 64):
                    col %= 64

                pixel = self.display.get(row, col-1)
                self.display.set(row, col-1, bit^pixel)
    def movL(self, v, x):
        self.v[v] = x

    def loadI(self, x):
        self.i = x

    def snel(self, x, y):
        if(self.v[x] != self.v[y]):
            self.pc += 2
            return True
        else:
            return False

    def toString(self):
        out = "Current OpCode:" + str(hex(self.opCode)) + "\n"
        out += "vR[" + str(self.i) + "]\n"
        for i in range(len(self.v)):
            out = out + "v" + str(i) + "[" + str(self.v[i]) + "]\t"

        out = out + "\n" + "Program Counter: " + str(self.pc) + "\n" + "Stack Pointer: " + str(self.sp) + "\n"
        return out

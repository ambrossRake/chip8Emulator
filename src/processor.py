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

    def __init__(self, display, keyboard):
        self.__memory = []
        self.__v = []
        self.__i = 0x0
        self.__pc = 0x200
        self.__stack = []
        self.__sp = 0x0
        self.__opCode = 0x0
        self.__isRunning = True
        self.__hertz = 500
        self.__clockSpeed = 1/self.__hertz
        self.__debugMode = True
        self.__pixels = []
        self.__dT = 0x0
        self.__sT = 0x0
        self.__display = display
        self.__keyboard = keyboard
        self.__font = [
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
            self.__memory.append(0x0)
        for _ in range(16):
            self.__v.append(0x0)
        for i in range(len(self.__font)):
            self.__memory[0x50+i] = self.__font[i]

    def reset(self):
        self.__memory = []
        self.__v = []
        self.__i = 0x0
        self.__pc = 0x200
        self.__stack = []
        self.__sp = 0x0
        self.__opCode = 0x0
        self.__dT = 0x0
        self.__sT = 0x0

        for _ in range(4096):
            self.__memory.append(0x0)
        for _ in range(16):
            self.__v.append(0x0)
        for i in range(len(self.__font)):
            self.__memory[0x50+i] = self.__font[i]

    def loadROM(self, rom):
        logger.info("Reading ROM into memory")
        for i in range(len(rom)):
            self.__memory[self.__pc+i] = rom[i]

    def emulateCycle(self):
        opCodeA = self.__memory[self.__pc]
        opCodeB = self.__memory[self.__pc+1]
        self.__opCode = int(opCodeA) << 8 | int(opCodeB)

        opA = self.__opCode & 0xF000
        opB = (self.__opCode & 0x0F00) >> 8
        opC = (self.__opCode & 0x00F0) >> 4
        opD = self.__opCode & 0x000F
        if(opA == 0x0000):
            if(self.__opCode & 0x00FF == 0x00EE):
                logger.info("Returning from sub routine")
                self.__ret()
            elif(opC == 0xE):
                logger.info("Clearing screen")
                self.__clr()
        elif(opA == 0x1000):
            addr = self.__opCode & 0x0FFF
            logger.info("Jumping to address: %s"%(hex(addr)))
            self.__jmp(addr)
        elif(opA == 0x2000):
            addr = self.__opCode & 0x0FFF
            logger.info("Calling subroutine at address %s"%(hex(addr)))
            self.__call(addr)
        elif(opA == 0x3000):
            skipped = self.__sex(opB, self.__opCode&0x00FF)
            if(skipped):
                logger.info("Skipping next instruction")
            else:
                logger.info("Ignoring Skip")
        elif(opA == 0x4000):
            const = self.__opCode&0x00FF
            logger.info("Checking if v[%d] != %d"%(opB,const))
            skipped = self.__sne(opB, const)
            if(skipped):
                logger.info("Skipping next instruction")
            else:
                logger.info("Ignoring skip")
        elif(opA == 0x5000):
            logger.info("Checking if %d == %d"%(opB,opC))
            skipped = self.__se(opB, opC)
            if(skipped):
                logger.info("Skipping next instruction")
            else:
                logger.info("Ignoring skip")
        elif(opA == 0x6000):
            const = self.__opCode&0x00FF
            logger.info("Moving constant %d into register v[%d]"%(const, opB))
            self.__movL(opB, const)
        elif(opA == 0x7000):
            const = self.__opCode&0x00FF
            logger.info("Adding constant %d to v[%d]"%(const, opB))
            self.__add(opB, const)
        elif(opA == 0x8000):
            if(opD == 0x0000):
                logger.info("Loading value from v[%d] into v[%d]"%(opC, opB))
                self.__ldxy(opB, opC)
            elif(opD == 0x0001):
                logger.info("v[%d] = v[%d] | v[%d]"%(opB,opB,opC))
                self.__orx(opB, opC)
            elif(opD == 0x0002):
                logger.info("v[%d] = v[%d] & v[%d]"%(opB,opB,opC))
                self.__andx(opB, opC)
            elif(opD == 0x0003):
                logger.info("v[%d] = v[%d] XOR v[%d]"%(opB, opB, opC))
                self.__xor(opB, opC)
            elif(opD == 0x0004):
                logger.info("Adding registers v[%d] and v[%d] into v[%d]"%(opB, opC, opB))
                self.__addc(opB, opC)
            elif(opD == 0x0005):
                logger.info("Subtracting v[%d] from v[%d]"%(opC, opB))
                self.__sub(opB, opC)
            elif(opD == 0x0006):
                logger.info("")
                self.__shr(opB, opC)
            elif(opD == 0x0007):
                #TODO: Add log
                self.__subn(opB, opC)
            elif(opD == 0x000E):
                self.__shl(opB, opC)
        elif(opA == 0x9000):
            skipped = self.__snel(opB, opC)
            if(skipped):
                logger.info("Skipping next instruction")
            else:
                logger.info("Skip ignored")

        elif(opA == 0xA000):
            const = self.__opCode&0x0FFF
            logger.info("Loading constant %d into index register"%(const))
            self.__loadI(const)

        elif(opA == 0xD000):
            self.__sprite(opB, opC, opD)

        elif(opA == 0xF000):
            opCD = self.__opCode & 0x00FF
            if(opCD == 0x0007):
                self.__loadXDT(opB)
            elif(opCD == 0x0015):
                self.__loadDT(opB)
            elif(opCD == 0x0029):
                logger.info("Setting vI to the address of sprite #" + str(self.__v[opB]))
                self.__loadFX(opB)
            elif(opCD == 0x0033):
                self.__bcd(opB)
            elif(opCD == 0x0055):
                self.__load0x(opB)
            elif(opCD == 0x0065):
                logger.info("Reading register v[0] through v[%d] from memory location %s"%(opB, hex(self.__i)))
                self.__loadXI(opB)
        elif(opA == 0xE000):
            opCD = self.__opCode & 0x00FF
            if(opCD == 0x009E):
                self.__skp(opB)
            elif(opCD == 0x00A1):
                self.__sknp(opB)
        else:
            self.isRunning = False
            logger.error("OpCode implementation for %s not found"%(hex(self.__opCode)))


        logger.info(str(self))
        self.__pc += 2

        if((self.__pc-0x200) % 60 == 0):
            if(self.__dT > 0):
                self.__dT -= 1
            if(self.__sT > 0):
                logger.info("BEEP")
                self.__sT -= 1

        self.__display.update()

    def __ldxy(self, x, y):
        self.__v[x] = self.__v[y]

    def __load0x(self, x):
        for i in range(x+1):
            self.__memory[self.__i+i] = self.__v[x]

    def __andx(self, x, y):
        self.__v[x] = self.__v[x] & self.__v[y]

    def __orx(self, x, y):
        self.__v[x] = self.__v[x] | self.__v[y]

    def __xor(self, x, y):
        self.__v[x] = self.__v[x] ^ self.__v[y]

    def __shr(self, x, y):
        self.__v[0xF] = self.__v[x] & 0b1
        self.__v[x] = math.floor(self.__v[x]/2)

    def __shl(self, x, y):
        logger.debug("self.v[0xF] = self.v[%d] >> 7 = %d"%(x, x>>7))
        logger.debug("self.v[0]=%d"%(self.__v[0]))
        self.__v[0xF] = self.__v[x] >> 7
        self.__v[x] *= 2
    def __subn(self, x, y):
        if(self.__v[y] > self.__v[x]):
            self.__v[y] -= self.__v[x]
            self.__v[0xF] = 1
        else:
            self.__v[0xF] = 0

    def __sub(self, x,y):
        if(self.__v[x] > self.__v[y]):
            self.__v[x] -= self.__v[y]
            self.__v[0xF] = 1
            return True
        else:
            self.__v[x] = 0xFF + (self.__v[x]-self.__v[y]) + 1
            self.__v[0xF] = 0
            return False

    def __add(self, v, const):
        sum = self.__v[v]+const
        print("SUM: %d"%(sum))
        if(sum < 0xFF):
            self.__v[v] = sum
        else:
            self.__v[v] = sum & 0xFF

    def __addc(self, x, y):
        sum = self.__v[x]+self.__v[y]
        if(sum < 0xFF):
            self.__v[x] = sum
            self.__v[0xF] = 0
        else:
            self.__v[x] = sum & 0xFF
            self.__v[0xF] = 1

        return self.__v[0xF]

    def __sne(self, v, x):
        if(self.__v[v] != x):
            self.__pc += 2
            return True
        else:
            return False

    def __se(self, x, y):
        if(self.__v[x] == self.__v[y]):
            self.__pc += 2
            return True
        else:
            return False
    def __loadXDT(self, v):
        logger.info("Placing delay timer value into register v[" + str(v) + "]")
        self.__v[v] = self.__dT

    def __loadDT(self, v):
        logger.info("Setting delay timer to " + str(v))
        self.__dT = self.__v[v]

    def __loadFX(self, v):
        self.__i = 0x50 + (self.__v[v] * 5)

    def __loadXI(self, x):
        for i in range(x+1):
            self.__v[i] = self.__memory[self.__i+i]

    def __jmp(self, x):
        if(x < len(self.__memory) and x > 0):
            self.__pc = x

    def __sex(self, v, x):
        if(self.__v[v] == x):
            self.__pc += 2
            return True
        else:
            return False

    def __ret(self):
        self.__pc = self.__stack.pop()
        self.__sp -= 1

    def __bcd(self, v):
        value = self.__v[v]
        logger.info("Storing value " + str(value) + " into memory locations{\n" + str(hex(self.__i)) + ", " + str(hex(self.__i+1)) + ", " + str(hex(self.__i+2)))
        ones = value % 10
        tens = (value / 10) % 10
        hundreds = value / 100
        self.__memory[self.__i] = math.floor(hundreds)
        self.__memory[self.__i+1] = math.floor(tens)
        self.__memory[self.__i+2] = math.floor(ones)

    def __call(self, addr):
        self.__sp += 1
        self.__stack.append(self.__pc)
        self.__pc = addr

    def __clr(self):
        self.__display.clear()

    def __sprite(self, x, y, n):
        logger.info("Drawing sprite at %d, %d with a height of %d"%(self.__v[x],self.__v[y],n))

        for i in range(n):
            byte = [int(a) for a in '{:08b}'.format(self.__memory[self.__i+i])]
            logger.debug("Reading byte #" + str(i) + ":")
            logger.debug(byte)
            for j in range(len(byte)):
                bit = byte[j]
                logger.debug("Bit: " + str(bit))
                row = self.__v[y]+i
                col = self.__v[x]+j
                if(row > 32):
                    row %= 32
                if(col > 64):
                    col %= 64

                pixel = self.__display.get(row, col)
                self.__display.set(row, col, bit^pixel)

    def __movL(self, v, x):
        self.__v[v] = x

    def __loadI(self, x):
        self.__i = x

    def __snel(self, x, y):
        if(self.__v[x] != self.__v[y]):
            self.__pc += 2
            return True
        else:
            return False

    def __skp(self, x):
        if(self.__keyboard.isKeyDown(x)):
            self.__pc += 2

    def __sknp(self, x):
        if(not self.__keyboard.isKeyDown(x)):
            self.__pc += 2

    def __str__(self):
        out = "Current OpCode:" + str(hex(self.__opCode)) + "\n"
        out += "vR[" + str(self.__i) + "]\n"
        for i in range(len(self.__v)):
            out = out + "v" + str(i) + "[" + str(self.__v[i]) + "]\t"

        out = out + "\n" + "Program Counter: " + str(self.__pc) + "\n" + "Stack Pointer: " + str(self.__sp) + "\n"
        return out

    def getClockSpeed(self):
        return self.__clockSpeed

    def setRegister(self, i, v):
        if(v <= 0xFFFFFFFF):
            self.__v[i] = v

    def getRegister(self, i):
        if(i < len(self.__v)):
            return self.__v[i]
        return None

    def getRegisters(self):
        return self.__v

    def getProgramCounter(self):
        return self.__pc

    def getMemory(self):
        return self.__memory

    def getIndexRegister(self):
        return self.__i

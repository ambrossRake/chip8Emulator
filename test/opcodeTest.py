import unittest
from processor import *

cpu = Processor(None)

class TestOpCodes(unittest.TestCase):

    def test1NNNValidAddr(self):
        addr = 0x10
        cpu.jmp(addr)
        self.assertEqual(addr, cpu.pc)


    def test1NNNMaxAddr(self):
        addr = 0xFFF
        cpu.jmp(addr)
        self.assertEqual(addr, cpu.pc)

    def test1NNNNegativeAddr(self):
        addr = -0x10
        prev = cpu.pc
        cpu.jmp(addr)
        self.assertEqual(cpu.pc, prev)

    def test1NNNOverflow(self):
        addr = 0xFFFFFFFF
        prev = cpu.pc
        cpu.jmp(addr)
        self.assertEqual(cpu.pc, prev)

    def testFX33ValidStore(self):
        num = 111
        cpu.v[0] = num
        cpu.bcd(0)
        x0 = cpu.memory[cpu.i]
        x1 = cpu.memory[cpu.i+1]
        x2 = cpu.memory[cpu.i+2]
        self.assertEqual(x0*100 + x1*10 + x2, num)

import unittest
import src.processor as p

cpu = p.Processor(None)
class TestOpCodes(unittest.TestCase):

    def setUp(self):
        cpu.reset()

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

    def test8XY6VFSetOn(self):
        num = 0b10101011
        cpu.v[0] = num
        cpu.shr(0,0)
        self.assertEqual(cpu.v[0xF], 1)

    def test8XY6VFSetOff(self):
        num = 0b10101010
        cpu.v[0] = num
        cpu.shr(0,0)
        self.assertEqual(cpu.v[0xF], 0)

    def test8XY6VXDivideByTwo(self):
        num = 0b10101011
        cpu.v[0] = num
        cpu.shr(0,0)
        self.assertEqual(cpu.v[0], num//2)

    def testFX55Store(self):
        for i in range(0xF):
            cpu.v[i] = 0xF8

        cpu.load0X(0xE)
        self.assertEqual(cpu.v[0:0xF], cpu.memory[cpu.i:cpu.i+0xF])

    def testFX65Load(self):
        for i in range(0xF):
            cpu.v[i] = 0xF8
        cpu.load0X(0xE)

        cpu.loadXI(0xE)
        self.assertEqual(cpu.v[0:0xF], cpu.memory[cpu.i:cpu.i+0xF])

    def testFX33ValidStore(self):
        num = 111
        cpu.v[0] = num
        cpu.bcd(0)
        x0 = cpu.memory[cpu.i]
        x1 = cpu.memory[cpu.i+1]
        x2 = cpu.memory[cpu.i+2]
        self.assertEqual(x0*100 + x1*10 + x2, num)

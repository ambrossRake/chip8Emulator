import unittest
import src.processor as p
import src.keyboard
import pynput
cpu = p.Processor(None, src.keyboard.Keyboard())
class TestOpCodes(unittest.TestCase):

    def setUp(self):
        cpu.reset()

    def test1NNNValidAddr(self):
        addr = 0x10
        cpu._Processor__jmp(addr)
        self.assertEqual(addr, cpu.getProgramCounter())

    def test1NNNMaxAddr(self):
        addr = 0xFFF
        cpu._Processor__jmp(addr)
        self.assertEqual(addr, cpu.getProgramCounter())

    def test1NNNNegativeAddr(self):
        addr = -0x10
        prev = cpu.getProgramCounter()
        cpu._Processor__jmp(addr)
        self.assertEqual(cpu.getProgramCounter(), prev)

    def test1NNNOverflow(self):
        addr = 0xFFFFFFFF
        prev = cpu.getProgramCounter()
        cpu._Processor__jmp(addr)
        self.assertEqual(cpu.getProgramCounter(), prev)

    def test8XY6VFEnabled(self):
        num = 0b10101011
        cpu.setRegister(0, num)
        cpu._Processor__shr(0,0)
        self.assertEqual(cpu.getRegister(0xF), 1)

    def test8XY6VFDisabled(self):
        num = 0b10101010
        cpu.setRegister(0, num)
        cpu._Processor__shr(0,0)
        self.assertEqual(cpu.getRegister(0xF), 0)

    def test8XY6VXDivideByTwo(self):
        num = 0b10101011
        cpu.setRegister(0, num)
        cpu._Processor__shr(0,0)
        self.assertEqual(cpu.getRegister(0), num//2)

    def testFX55Store(self):
        for i in range(0xF):
            cpu.setRegister(i, 0xF8)

        cpu._Processor__load0x(0xE)
        self.assertEqual(cpu.getRegisters()[0 : 0xF], cpu.getMemory()[cpu.getIndexRegister() : cpu.getIndexRegister()+0xF])

    def testFX65Load(self):
        for i in range(0xF):
            cpu.setRegister(i, 0xF8)

        cpu._Processor__load0x(0xE)
        cpu._Processor__loadXI(0xE)
        self.assertEqual(cpu.getRegisters()[0 : 0xF], cpu.getMemory()[cpu.getIndexRegister() : cpu.getIndexRegister()+0xF])

    def testFX33ValidStore(self):
        num = 111
        cpu.setRegister(0, num)
        cpu._Processor__bcd(0)
        x0 = cpu.getMemory()[cpu.getIndexRegister()]
        x1 = cpu.getMemory()[cpu.getIndexRegister()+1]
        x2 = cpu.getMemory()[cpu.getIndexRegister()+2]
        self.assertEqual(x0*100 + x1*10 + x2, num)

    def test8XYEVFEnabled(self):
        num = 0b10101011
        cpu.setRegister(0x0, num)
        cpu._Processor__shl(0x0,0x0)
        self.assertEqual(cpu.getRegister(0xF),0x1)

    def test8XYEVFDisabled(self):
        num = 0b00101010
        cpu.setRegister(0x0, num)
        cpu._Processor__shl(0x0,0x0)
        self.assertEqual(cpu.getRegister(0xF),0x0)

    def test8XYEMultiplyByTwo(self):
        num = 0b10101011
        cpu.setRegister(0x0, num)
        cpu._Processor__shl(0x0,0x0)
        self.assertEqual(cpu.getRegister(0x0), num*2)

    def testEX9ESkipOnKeyDown(self):
        pastPC = cpu.getProgramCounter()
        pynput.keyboard.Controller().press('1')
        cpu._Processor__skp(1)
        pynput.keyboard.Controller().release('1')
        self.assertEqual(pastPC+2,cpu.getProgramCounter())

    def testEXA1SkipOnKeyUp(self):
        pastPC = cpu.getProgramCounter()
        pynput.keyboard.Controller().release('1')
        cpu._Processor__sknp(1)
        self.assertEqual(pastPC+2,cpu.getProgramCounter())

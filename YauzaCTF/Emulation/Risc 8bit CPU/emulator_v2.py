class Runner:
    def __init__(self, code):
        self.code = code + [0x00] * (0xFFFF - len(code))
        assert(len(self.code) == 0xFFFF)
        self.pc = 0x1000
        self.r = [0, 0, 0]
        self.flag = 0

        self.optmap = {
            0: self._add,
            1: self._xor,
            2: self._and,
            3: self._or,
            4: self._ld,
            5: self._mov,
            6: self._ldr_kk,
            7: self._ldr,
            8: self._str_kkkk,
            9: self._str,
            10: self._put,
            11: self._jmp,
            12: self._jnz,
            13: self._jz,
            14: self._cmpeq,
            0x44: self._hlt,
            0x33: self._nop
        }
    
    def _add(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")

        self.r[op1] = (self.r[op1] + op3) & 0xFF
        
    
    def _xor(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")
        
        self.r[op1] ^= op3
    
    def _and(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")
        
        self.r[op1] &= op3
    
    def _or(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")
        
        self.r[op1] |= op3
    
    def _ld(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")
        
        self.r[op1] = op3
    
    def _mov(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not 0x00 <= op3 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")
        
        self.r[op1] = self.r[op3]
    
    def _ldr_kk(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        
        self.r[op1] = self.code[(op2 << 8) | op3]
    
    def _ldr(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")
        if not op3 == 0:
            raise ValueError("Wrong op3 info")
        
        self.r[op1] = self.code[(self.r[1] << 8) | self.r[2]]
    
    def _str_kkkk(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        
        self.code[(op2 << 8) | op3] = self.r[op1]
    
    def _str(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")
        if not op3 == 0:
            raise ValueError("Wrong op3 info")
        
        self.code[(self.r[1] << 8) | self.r[2]] = self.r[op1]
    
    def _put(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")
        if not op3 == 0:
            raise ValueError("Wrong op3 info")
        
        print(chr(self.r[op1]), end='')
    
    def _jmp(self, op1, op2, op3):
        if op1 != 0:
            raise ValueError("Wrong op1 info")

        self.pc = (op2 << 8) | op3
        #self.pc -= 4
    
    def _jnz(self, op1, op2, op3):
        if op1 != 0:
            raise ValueError("Wrong op1 info")
        
        if self.flag == 0:
            self.pc = (op2 << 8) | op3
            #self.pc -= 4
    
    def _jz(self, op1, op2, op3):
        if op1 != 0:
            raise ValueError("Wrong op1 info")
        
        if self.flag == 1:
            self.pc = (op2 << 8) | op3
            #self.pc -= 4
    
    def _cmpeq(self, op1, op2, op3):
        if not 0x00 <= op1 <= 0x02:
            raise ValueError("Wrong register info")
        if not op2 == 0:
            raise ValueError("Wrong op2 info")
        
        self.flag = int(self.r[op1] == op3)
    
    def _hlt(self, op1, op2, op3):
        if not (op1 == 0x44 and op2 == 0x44 and op3 == 0x44):
            raise ValueError("Wrong op info")

        print("stop")
        while True:
            pass

    def _nop(self, op1, op2, op3):
        if not (op1 == 0x33 and op2 == 0x33 and op2 == 0x33):
            raise ValueError("Wrong op info")

    def run(self):
        while True:
            optcode = self.optmap[self.code[self.pc]]
            ops = self.code[self.pc + 1: self.pc + 4]
            optcode(*ops)
            self.pc += 4

runner = Runner(list(open("rom.bin", "rb").read()))
runner.run()

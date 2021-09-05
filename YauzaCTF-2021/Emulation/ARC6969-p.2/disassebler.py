from Crypto.Util.number import bytes_to_long, long_to_bytes
import sys


class Runner:
    def __init__(self, code):
        self.code = code + [0x00] * (0xFFFF - len(code))

        self.pc = 0x00
        self.r = [0] * 32
        self.flag = [0] * 8

        self.ZF = 0
        self.CF = 1
        self.SF = 2
        self.OF = 3
        self.screen = [[0 for _ in range(64)] for __ in range(32)]
        self.screen_buffer = [[-1 for _ in range(64)] for __ in range(32)]
        self.buffer_x = 0
        self.buffer_y = 0

        self.optmap_arithm = {
            0: self._add,
            1: self._addi,
            2: self._sub,
            3: self._subi,
            6: self._or,
            7: self._ori,
            8: self._xor,
            9: self._xori,
            10: self._and,
            11: self._andi,
            12: self._shl,
            13: self._shr,
        }

        self.optmap_comp = {
            4: self._cmp,
            5: self._cmpi
        }

        self.optmap_flow = {
            24: self._call,
            25: self._ret,
            16: self._jmp,
            17: self._je,
            18: self._jne,
            19: self._jb,
            20: self._jl,
            26: self._jg,
            27: self._ja
        }

        self.optmap_mem = {
            14: self._rd,
            15: self._wr
        }

        self.iomap = {
            1: self._io_gpu_set_x,
            2: self._io_gpu_set_y,
            3: self._io_gpu_draw,
            4: self._io_gpu_update,
            5: self._io_serial_length,
            6: self._io_serial_read,
            7: self._io_serial_write
        }

    def _add (self, op1, op2, op3):
        print(f"ADD R{op1} R{op2} R{op3}")

    def _addi (self, op1, op2, op3):
        print(f"ADD R{op1} R{op2} {op3:02x}")

    def _sub (self, op1, op2, op3):
        print(f"SUB R{op1} R{op2} R{op3}")

    def _subi (self, op1, op2, op3):
        print(f"SUB R{op1} R{op2} {op3:02x}")

    def _or (self, op1, op2, op3):
        print(f"OR R{op1} R{op2} R{op3}")

    def _ori (self, op1, op2, op3):
        print(f"OR R{op1} R{op2} {op3:02x}")

    def _xor (self, op1, op2, op3):
        print(f"XOR R{op1} R{op2} R{op3}")

    def _xori (self, op1, op2, op3):
        print(f"XOR R{op1} R{op2} {op3:02x}")

    def _and (self, op1, op2, op3):
        print(f"AND R{op1} R{op2} R{op3}")

    def _andi (self, op1, op2, op3):
        print(f"AND R{op1} R{op2} {op3:02x}")

    def _shl (self, op1, op2, op3):
        print(f"SHL R{op1} R{op2} R{op3}")

    def _shr (self, op1, op2, op3):
        print(f"SHR R{op1} R{op2} R{op3}")

    def _cmp (self, op1, op2):
        print(f"CMP R{op1} R{op2}")

    def _cmpi (self, op1, op2):
        print(f"CMPI R{op1} {op2:02x}")

    def _call (self, op1):
        print(f"CALL {op1:02x}")

    def _ret (self, op1):
        print(f"RET")

    def _jmp (self, op1):
        print(f"JMP {op1:02x}")

    def _je (self, op1):
        print(f"JE {op1:02x}")

    def _jne (self, op1):
        print(f"JNE {op1:02x}")

    def _jb (self, op1):
        print(f"JB {op1:02x}")

    def _jl (self, op1):
        print(f"JL {op1:02x}")

    def _jg (self, op1):
        print(f"JG {op1:02x}")

    def _ja (self, op1):
        print(f"JA {op1:02x}")

    def _rd (self, op1, op2, op3):
        print(f"RD R{op1} R{op2} R{op3}")

    def _wr (self, op1, op2, op3):
        print(f"WR R{op1} R{op2} R{op3}")

    def _io_gpu_set_x (self, op1):
        print(f"IO_GPU_SET_X R{op1}")

    def _io_gpu_set_y (self, op1):
        print(f"IO_GPU_SET_Y R{op1}")

    def _io_gpu_draw (self, op1):
        print(f"IO_GPU_DRAW R{op1}")

    def _io_gpu_update (self, op1):
        print(f"IO_GPU_SET_X R{op1}")
                    
    def _io_serial_length (self, op1):
        print(f"IO_SERIAL_LENGTH R{op1}")

    def _io_serial_read (self, op1):
        print(f"IO_SERIAL_READ R{op1}")

    def _io_serial_write (self, op1):
        print(f"IO_SERIAL_WRITE R{op1}")

    def run(self):
        while self.pc < len(self.code) - 2:
            instruction = bytes_to_long(bytes(self.code[self.pc:self.pc + 3]))
            optcode = (self.code[self.pc] >> 3) & 0b11111
            print(f"{self.pc:>04x}    ", end='')

            
            if optcode in self.optmap_arithm.keys():
                instruction = bytes_to_long(bytes(self.code[self.pc:self.pc + 3]))
                self.pc += 3

                op1 = (instruction >> 13) & 0b11111
                op2 = (instruction >> 8) & 0b11111
                op3 = instruction & ((1 << 8) - 1)

                self.optmap_arithm[optcode](op1, op2, op3)
            elif optcode in self.optmap_comp.keys():
                instruction = bytes_to_long(bytes(self.code[self.pc:self.pc + 3]))
                self.pc += 3

                op1 = (instruction >> 11) & 0b11111
                op2 = instruction & ((1 << 8) - 1)

                self.optmap_comp[optcode](op1, op2)
            elif optcode in self.optmap_flow.keys():
                instruction = bytes_to_long(bytes(self.code[self.pc:self.pc + 3]))
                self.pc += 3

                op1 = instruction & ((1 << 16) - 1)

                self.optmap_flow[optcode](op1)
            elif optcode in self.optmap_mem.keys():
                instruction = bytes_to_long(bytes(self.code[self.pc:self.pc + 3]))
                self.pc += 3

                op1 = (instruction >> 13) & 0b11111
                op2 = (instruction >> 8) & 0b11111
                op3 = instruction & 0b11111

                self.optmap_mem[optcode](op1, op2, op3)
            elif optcode == 21:
                instruction = bytes_to_long(bytes(self.code[self.pc:self.pc + 2]))
                self.pc += 2

                index = instruction & 0b111
                op1 = (instruction >> 3) & 0b11111

                self.iomap[index](op1)
            if self.pc == 948:
                break


runner = Runner(list(open("rom_2.bin", "rb").read()))
runner.run()
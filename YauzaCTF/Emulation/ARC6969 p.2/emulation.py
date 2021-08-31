#!/bin/env/python
from Crypto.Util.number import bytes_to_long, long_to_bytes
import sys
import pygame
from time import sleep


class Runner:
    def __init__(self, code):
        self.code = code + [0x00] * (0xFFFF - len(code))

        pygame.init()
        self.surface = pygame.display.set_mode((640, 320))
        self.rects = [[pygame.Rect(x * 10, y * 10, 10, 10)for x in range(64)] for y in range(32)]

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
        self.input_buffer = ""

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
        self.r[op1] = (self.r[op2] + self.r[op3]) & 0xFF

    def _addi (self, op1, op2, op3):
        self.r[op1] = (self.r[op2] + op3) & 0xFF

    def _sub (self, op1, op2, op3):
        tmp = (self.r[op3] ^ 0xFF) + 1
        self.r[op1] = (self.r[op2] + tmp) & 0xFF

    def _subi (self, op1, op2, op3):
        tmp = (op3 ^ 0xFF) + 1
        self.r[op1] = (self.r[op2] + tmp) & 0xFF

    def _or (self, op1, op2, op3):
        self.r[op1] = self.r[op2] | self.r[op3]

    def _ori (self, op1, op2, op3):
        self.r[op1] = self.r[op2] | op3

    def _xor (self, op1, op2, op3):
        self.r[op1] = self.r[op2] ^ self.r[op3]

    def _xori (self, op1, op2, op3):
        self.r[op1] = self.r[op2] ^ op3

    def _and (self, op1, op2, op3):
        self.r[op1] = self.r[op2] & self.r[op3]

    def _andi (self, op1, op2, op3):
        self.r[op1] = self.r[op2] & op3

    def _shl (self, op1, op2, op3):
        self.r[op1] = self.r[op2] << self.r[op3]

    def _shr (self, op1, op2, op3):
        self.r[op1] = self.r[op2] >> self.r[op3]

    def _true_num(self, num):
        if (num >> 7) & 1 == 0:
            return num
        else:
            return -((num ^ 0xFF) + 1)

    def _cmp (self, op1, op2):
        self.flag[self.ZF] = self.r[op1] == self.r[op2]
        self.flag[self.CF] = self.r[op1] < self.r[op2]
        self.flag[self.SF] = ((self.r[op1] + (self.r[op2] ^ 0xFF) + 1) >> 7) & 1
        self.flag[self.OF] = int(not -128 <= self._true_num(self.r[op1]) - self._true_num(self.r[op2]) <= 127)

    def _cmpi (self, op1, op2):
        self.flag[self.ZF] = self.r[op1] == op2
        self.flag[self.CF] = self.r[op1] < op2
        self.flag[self.SF] = ((self.r[op1] + (op2 ^ 0xFF) + 1) >> 7) & 1
        self.flag[self.OF] = int(not -128 <= self._true_num(self.r[op1]) - self._true_num(op2) <= 127)

    def _call (self, op1):
        self.r[31] = self.pc
        self._jmp(op1)

    def _ret (self, op1):
        self._jmp(self.r[31])

    def _jmp (self, op1):
        self.pc = op1

    def _je (self, op1):
        if self.flag[self.ZF] == 1:
            self._jmp(op1)

    def _jne (self, op1):
        if self.flag[self.ZF] == 0:
            self._jmp(op1)

    def _jb (self, op1):
        if self.flag[self.CF] == 1:
            self._jmp(op1)

    def _jl (self, op1):
        if self.flag[self.SF] != self.flag[self.OF]:
            self._jmp(op1)

    def _jg (self, op1):
        if self.flag[self.ZF] == 0 and self.flag[self.OF] == self.flag[self.SF]:
            self._jmp(op1)

    def _ja (self, op1):
        if self.flag[self.CF] == 0 and self.flag[self.ZF] == 0:
            self._jmp(op1)

    def _rd (self, op1, op2, op3):
        self.r[op1] = self.code[(self.r[op2] << 8) | self.r[op3]]

    def _wr (self, op1, op2, op3):
        self.code[(self.r[op2] << 8) | self.r[op3]] = self.r[op1]

    def _io_gpu_set_x (self, op1):
        self.buffer_x = self.r[op1]

    def _io_gpu_set_y (self, op1):
        self.buffer_y = self.r[op1]

    def _io_gpu_draw (self, op1):
        self.screen_buffer[self.buffer_y][self.buffer_x] = self.r[op1]

    def _normalize_color(self, color):
        red = (color >> 4) & 0b11
        green = (color >> 2) & 0b11
        blue = color & 0b11

        return (int(255 / 4 * red), int(255 / 4 * green), int(255 / 4 * blue))

    def _io_gpu_update (self, op1):
        for y in range(32):
            for x in range(64):
                if self.screen_buffer[y][x] != -1:
                    self.screen[y][x] = self.screen_buffer[y][x]
                    self.screen_buffer[y][x] = -1

                    pygame.draw.rect(self.surface, self._normalize_color(self.screen[y][x]), self.rects[y][x])
        sleep(0.01)
        pygame.display.flip()
                    
        
    def _io_serial_length (self, op1):
        self.input_buffer += input()
        self.r[op1] = len(self.input_buffer)

    def _io_serial_read (self, op1):
        self.r[op1] = ord(self.input_buffer[0])
        self.input_buffer = self.input_buffer[1:]

    def _io_serial_write (self, op1):
        sys.stdout.write(chr(self.r[op1]))

    def run(self):
        while True:
            instruction = bytes_to_long(bytes(self.code[self.pc:self.pc + 3]))
            optcode = (self.code[self.pc] >> 3) & 0b11111
            print(self.pc)

            
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
            else:
                sys.stdout.write('\n')
                break


runner = Runner(list(open("rom_2.bin", "rb").read()))
runner.run()

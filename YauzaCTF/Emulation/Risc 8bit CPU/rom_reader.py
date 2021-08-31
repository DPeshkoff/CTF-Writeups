rom = open("rom.bin", "rb").read()

reg_1 = 0
reg_2 = 0
reg_3 = 0

for i in range(0x1000, 0x1100, 4):
    print(f"{i:<8x}", end='')
    if rom[i] == 0x00:
        print(f"ADD R{rom[i + 1]}, {rom[i + 3]:02x}")
        
    if rom[i] == 0x01:
        print(f"XOR R{rom[i + 1]}, {rom[i + 3]:02x}")
    if rom[i] == 0x02:
        print(f"AND R{rom[i + 1]}, {rom[i + 3]:02x}")
    if rom[i] == 0x03:
        print(f"OR R{rom[i + 1]},  {rom[i + 3]:02x}")
    if rom[i] == 0x04:
        print(f"LD R{rom[i + 1]}, {rom[i + 3]:02x}")
    if rom[i] == 0x05:
        print(f"MOV R{rom[i + 1]}, R{rom[i + 3]}")
    if rom[i] == 0x06:
        print(f"LDR R{rom[i + 1]}, {rom[i + 2]:02x}{rom[i + 3]:02x}")
    if rom[i] == 0x07:
        print(f"LDR R{rom[i + 1]}")
    if rom[i] == 0x08:
        print(f"STR R{rom[i + 1]}, {rom[i + 2]:02x}{rom[i + 3]:02x}")
    if rom[i] == 0x09:
        print(f"STR R{rom[i + 1]}")
    if rom[i] == 0x0A:
        print(f"PUT R{rom[i + 1]}")
    if rom[i] == 0x0B:
        print(f"JMP {rom[i + 2]:02x}{rom[i + 3]:02x}")
    if rom[i] == 0x0C:
        print(f"JNZ {rom[i + 2]:02x}{rom[i + 3]:02x}")
    if rom[i] == 0x0D:
        print(f"JZ {rom[i + 2]:02x}{rom[i + 3]:02x}")
    if rom[i] == 0x0E:
        print(f"CMPEQ R{rom[i + 1]}, {rom[i + 3]:02x}")
    if rom[i] == 0x44:
        print("HLT")
    if rom[i] == 0x33:
        print("NOP")
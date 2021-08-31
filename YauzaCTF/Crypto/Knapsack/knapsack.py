import string
from itertools import product

flag = [12777998288638, 10593582832873, 7834439533378, 10486500991495, 14714582460036, 7568907598905, 12800035735033, 14724457772647, 11910445040159, 11202963622894, 10291238568620, 15103559399914, 13156142631772, 16988824411176]
pubkey = [2948549611747, 2043155587142, 361533419625, 1001380428657, 2438250374319, 1059738568330, 115120002311, 198226659880, 2343897184958, 2592576935132, 2327834076450, 237536244289, 309228208827, 3327276767693, 462372704541, 2176574227058]

def encrypt_num(n):
    n = "{:016b}".format(n)
    sum_p = 0
    for i, val in zip(map(int, n), pubkey):
        sum_p += i * val
    return sum_p

letters = string.printable[:-6]

hash_table = dict()

for i, j in list(product(letters, letters)):
    hash_table[encrypt_num((ord(i) << 8) + ord(j))] = i + j

for i in flag:
    print(hash_table[i], end='')
else:
    print()

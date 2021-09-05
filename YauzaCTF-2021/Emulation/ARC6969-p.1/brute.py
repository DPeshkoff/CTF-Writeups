from subprocess import Popen, PIPE
from itertools import product
import string
from tqdm import tqdm

s = list(map(ord, string.printable[:-6]))
l = [100, 76, 64, 67, 76, 242, 97, 239, 42, 245, 2, 57, 57, 253, 78, 79, 59, 253, 56, 78, 252, 4, 255, 4, 78, 58, 252, 81, 81, 253, 40]

for i, j, k in tqdm(list(product(s, s, s))):
    if ''.join(map(lambda a: str(((((a + i) & 0xFF) ^ j) + (k ^ 0xFF) + 1) & 0xFF), l[:9])) == ''.join(map(lambda a: str(ord(a)), 'YauzaCTF{')):
        print(''.join(map(lambda a: chr((((((a + i) & 0xFF) ^ j) + (k ^ 0xFF) + 1) & 0xFF)), l)))
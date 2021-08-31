from Crypto.Hash import SHA256
from Crypto.Util.number import bytes_to_long, long_to_bytes, size, getRandomNBitInteger
from storage import flag

def byten(x, n):
    return (x >> (n * 8)) & 0xFF

def mask(n):
    return (1 << n) - 1

def rotate(x, n, s):
    return ((x >> (s - n)) | (x << n)) & mask(s)

def scramble(x):
    magic = 0xC3A569C3A569C3A569C3A569C3A569C33C965A3C965A3C965A3C965A3C965A3C
    for i in range(32):
        x = rotate(x, 27, 256) ^ rotate(magic, i, 256)
    return x

def sha2(x):
    hash = SHA256.new()
    hash.update(x)
    return hash.digest()

def gen_pair():
    private = [getRandomNBitInteger(256) for _ in range(16)]
    public = [long_to_bytes(y) for y in private]
    for i in range(16):
        for j in range(255):
            public[i] = sha2(public[i])
    return private, [bytes_to_long(y) for y in public]


def sign(x, key):
    parts = [byten(x, i) for i in range(16)]

    digest = [long_to_bytes(y) for y in key]
    for i in range(16):
        for j in range(parts[i]):
            digest[i] = sha2(digest[i])

    return digest

def verify(x, sign, public):
    parts = [255 - byten(x, i) for i in range(16)]

    digest = list(sign)
    for i in range(16):
        for j in range(parts[i]):
            digest[i] = sha2(digest[i])
        if digest[i] != long_to_bytes(public[i]):
            return False
    return True


def do_signature(x, private):
    signature = sign(scramble(x), private)
    return bytes_to_long(b''.join(signature))

def do_verify(x, signature, public):
    signature = long_to_bytes(signature, 256*16//8)
    signature = [signature[i*32:(i + 1)*32] for i in range(16)]
    return verify(scramble(x), signature, public)


menu = '''\
[1] Sign message
[2] Get flag
[3] Quit'''

if __name__ == '__main__':
    private, public = gen_pair()
    challenge = getRandomNBitInteger(256)
    while True:
        try:
            print(menu)
            opt = input('> ')
            if opt == '1':
                data = int(input('msg: '))
                if size(data) > 256:
                    raise Exception('Message is too long (256 bits max)')
                if data == challenge:
                    raise Exception('Nice try')

                print(do_signature(data, private))
            elif opt == '2':
                print('Enter signature for the message:')
                print(challenge)
                data = int(input('sign: '))
                if size(data) > 256*16:
                    raise Exception('Signature is too long (16 blocks, 256 bits each)')
                if not do_verify(challenge, data, public):
                    raise Exception('Wrong signature')
                print(flag)
            elif opt == '3':
                exit(0)
            else:
                raise Exception('Unknown option')
        except Exception as ex:
            print('Error:', ex)


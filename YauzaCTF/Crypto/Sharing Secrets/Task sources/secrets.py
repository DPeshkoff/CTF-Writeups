import json

from Crypto.Util.number import bytes_to_long, getPrime
from storage import flag


def mul(x):
    m = 1
    for i in x:
        m *= i
    return m


if __name__ == '__main__':
    flag = bytes_to_long(flag.encode())

    count = 25
    threshold = 11
    psize = 24

    primes = list(sorted(getPrime(psize) for _ in range(count)))

    pmin = mul(primes[-threshold + 1:])
    pmax = mul(primes[:threshold])

    assert pmin < flag < pmax

    shadows = [flag % x for x in primes]

    with open('secrets.json', 'wt') as out_file:
        out_file.write(json.dumps({
            'shadows': shadows[1:threshold],
            'primes': primes[:threshold],
            'threshold': threshold
        }))

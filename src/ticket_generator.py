from web3 import Web3
from fastecdsa.point import Point
from fastecdsa.curve import secp256k1

import random


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception("modular inverse does not exist")
    else:
        return x % m


def generate_signature(msg_hash: int, signing_key: int):
    N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    GenPoint = Point(Gx, Gy, curve=secp256k1)

    rand_num = random.randint(99999, 999999999999)
    xy1 = rand_num * GenPoint
    r = xy1.x % N
    s = ((msg_hash + r * signing_key) * modinv(rand_num, N)) % N
    return r, s


if __name__ == "__main__":
    group_id = int(input("[+] Group ID: ").strip(), 16)
    node_id = int(input("[+] Node ID: ").strip(), 16)
    node_addr = input("[+] Node public address: ")
    assert Web3.isAddress(node_addr) is True, "[x] Node address is invalid!"

    master_key = int(input("[+] Master private key: "), 16)
    hash_data = Web3.solidityKeccak(
        ["uint8", "uint8", "address"],
        [group_id, node_id, Web3.toChecksumAddress(node_addr)],
    )
    r, s = generate_signature(Web3.toInt(hash_data), master_key)
    print(f"[>] r: {r}")
    print(f"[>] s: {s}")

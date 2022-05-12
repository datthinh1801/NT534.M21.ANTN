import struct

from Crypto.Hash import keccak


def hash_keccak(input_byte) -> int:
    k = keccak.new(digest_bits=256)
    k.update(input_byte)
    return int(k.hexdigest(), 16)


group_id = int(input("[+] Group ID: ").strip()[:2], 16)
node_id = int(input("[+] Node ID: ").strip()[:2], 16)
node_addr = int(input("[+] Node public address: "), 16)
master_pub_key = int(input("[+] Master public key: "), 16)

# concat groupID|nodeID|nodePubAddr
ids = struct.pack(">BB", group_id, node_id)
node_addr_bytes = node_addr.to_bytes(20, "big")
tosign_data = ids + node_addr_bytes

hash_data = hash_keccak(tosign_data)
hash_master_key = hash_keccak(master_pub_key.to_bytes(20, "big"))

signed_data = hash_data ^ hash_master_key
print(f"[>] Ticket: {signed_data}")

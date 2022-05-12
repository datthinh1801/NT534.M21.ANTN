from web3 import Web3

if __name__ == "__main__":
    group_id = int(input("[+] Group ID: ").strip(), 16)
    node_id = int(input("[+] Node ID: ").strip(), 16)
    node_addr = int(input("[+] Node public address: "), 16)
    master_pub_key = int(input("[+] Master public key: "), 16)

    hash_data = Web3.solidityKeccak(
        ["uint8", "uint8", "address"],
        [group_id, node_id, Web3.toChecksumAddress(hex(node_addr))],
    )
    hash_master_key = Web3.solidityKeccak(
        ["address"], [Web3.toChecksumAddress(hex(master_pub_key))]
    )

    signed_data = Web3.toInt(hash_data) ^ Web3.toInt(hash_master_key)
    print(f"[>] Ticket (hex): {hex(signed_data)}")
    print(f"[>] Ticket (uint): {signed_data}")

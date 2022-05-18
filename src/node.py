from utils import *


if __name__ == "__main__":
    w3, abi, bytecode = init_contract()
    node_addr = input("[+] Node public address: ")
    assert Web3.isAddress(node_addr) is True, "[x] Address is invalid!"

    contract_addr = input("[+] Contract address: ")
    assert Web3.isAddress(contract_addr) is True, "[x] Address is invalid!"

    contract_instance = w3.eth.contract(address=contract_addr, abi=abi)
    node_data = {"pub_addr": node_addr, "node_id": None, "group_id": None}

    while True:
        print("-" * 50)
        print("[+] Select an option:")
        print("[1] Add node")
        print("[2] Send a message")
        print("[3] Read messages")
        print("[q] Quit")

        try:
            selection = int(input("[>] "))
        except:
            if selection == "q":
                print("[!] Exiting...")
            else:
                print("[x] Invalid selection!")
            break

        if selection == 1:
            if contract_instance.functions.membersGrpId(node_addr).call() != 0:
                print("[!] Node already registered!")
                continue

            category = int(input("[+] Node type (0: master, 1: slave): "))
            group_id = int(input("[+] Group ID (hex): "), 16)
            node_id = int(input("[+] Node ID (hex): "), 16)
            ticket = 0

            if category == 1:
                ticket = int(input("[+] Ticket (hex): "), 16)

            try:
                tx_hash = contract_instance.functions.BCTrustV2_AddNode(
                    category, group_id, node_id, ticket
                ).transact(
                    {
                        "from": node_addr,
                        "to": contract_addr,
                    }
                )
                w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"[+] Transaction hash: {Web3.toHex(tx_hash)}")
                node_data["node_id"] = node_id
                node_data["group_id"] = group_id
            except:
                print("[x] Node or group already exists!")
        elif selection == 2:
            if node_data["node_id"] is None:
                sender_id = int(input("[+] Sender ID (hex): "), 16)
            else:
                sender_id = node_data["node_id"]

            receiver_id = int(input("[+] Receiver ID (hex): "), 16)
            message = input("[+] Message: ")

            try:
                tx_hash = contract_instance.functions.BCTrustV2_Send(
                    sender_id, receiver_id, message
                ).transact(
                    {
                        "from": node_addr,
                        "to": contract_addr,
                    }
                )
                w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"[+] Transaction hash: {Web3.toHex(tx_hash)}")
            except:
                print(f"[x] Sender and receiver are from different groups!")
        elif selection == 3:
            if node_data["node_id"] is None:
                node_id = int(input("[+] Node ID (hex): "), 16)
            else:
                node_id = node_data["node_id"]
                message = contract_instance.functions.messages(node_id).call()
                if len(message) > 0:
                    print(f"[msg] {message}")
                else:
                    print("[!] No messages!")
                try:
                    tx_hash = contract_instance.functions.BCTrustV2_ClearMSG(
                        node_id
                    ).transact(
                        {
                            "from": node_addr,
                            "to": contract_addr,
                        }
                    )
                except:
                    pass
        else:
            print("[x] Invalid selection!")
            break

from colorama import Fore, Style
from utils import *


if __name__ == "__main__":
    w3, abi, bytecode = init_contract()
    node_addr = input("[+] Node public address: ")
    assert Web3.isAddress(node_addr) is True, Fore.RED + "[x] Address is invalid!"

    contract_addr = input("[+] Contract address: ")
    assert Web3.isAddress(contract_addr) is True, Fore.RED + "[x] Address is invalid!"

    contract_instance = w3.eth.contract(address=contract_addr, abi=abi)
    group_id = contract_instance.functions.membersGrpId(node_addr).call()
    node_id = contract_instance.functions.membersId(node_addr).call()
    node_data = {"pub_addr": node_addr, "node_id": node_id, "group_id": group_id}

    while True:
        print(Style.RESET_ALL, end="")
        print("-" * 50)
        print("[+] Select an option:")
        print("[1] Add node")
        print("[2] Send a message")
        print("[3] Read messages")
        print("[q] Quit")
        selection = input("[>] ").strip()

        try:
            selection = int(selection)
        except:
            if selection == "q":
                print(Fore.YELLOW + "[!] Exiting...")
            else:
                print(Fore.RED + "[x] Invalid selection!")
            break

        if selection == 1:
            if node_data["group_id"] != 0:
                print(Fore.YELLOW + "[!] Node already registered!")
                continue

            while True:
                category = int(input("[+] Node type (0: master, 1: slave): "))
                if category in [0, 1]:
                    break
                else:
                    print(Fore.YELLOW + "[!] Invalid selection!" + Style.RESET_ALL)
            while True:
                group_id = int(input("[+] Group ID (hex): "), 16)
                if group_id > 0:
                    break
                else:
                    print(
                        Fore.YELLOW
                        + "[!] Group ID must be greater than 0!"
                        + Style.RESET_ALL
                    )
            while True:
                node_id = int(input("[+] Node ID (hex): "), 16)
                if node_id > 0:
                    break
                else:
                    print(
                        Fore.YELLOW
                        + "[!] Node ID must be greater than 0!"
                        + Style.RESET_ALL
                    )

            r = 0
            s = 0

            if category == 1:
                r = int(input("[+] Ticket (int r): "))
                s = int(input("[+] Ticket (int s): "))

            try:
                tx_hash = contract_instance.functions.BCTrustV2_AddNode(
                    category, group_id, node_id, r, s
                ).transact(
                    {
                        "from": node_addr,
                        "to": contract_addr,
                    }
                )
                w3.eth.wait_for_transaction_receipt(tx_hash)
                print(Fore.GREEN + f"[+] Transaction hash: {Web3.toHex(tx_hash)}")
                node_data["node_id"] = node_id
                node_data["group_id"] = group_id
            except:
                print(Fore.RED + "[x] Association failed!")
        elif selection == 2:
            if node_data["node_id"] == 0:
                print(Fore.YELLOW + "[!] Node not registered!")
                continue

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
                print(Fore.GREEN + f"[+] Transaction hash: {Web3.toHex(tx_hash)}")
            except:
                print(Fore.RED + f"[x] Sender and receiver are from different groups!")
        elif selection == 3:
            if node_data["node_id"] == 0:
                print(Fore.YELLOW + "[!] Node not registered!")
                continue

            node_id = node_data["node_id"]
            message = contract_instance.functions.messages(node_id).call()
            if len(message) > 0:
                print(Fore.GREEN + f"[msg] {message}")
            else:
                print(Fore.YELLOW + "[!] No new messages!")
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
            print(Fore.YELLOW + "[x] Invalid selection!")
            break

from colorama import Fore, Style
from ticket_generator import generate_signature
from utils import *

import time


if __name__ == "__main__":
    # init the smart contract
    w3, abi, _ = init_contract()
    # read node data
    node_addr = input("[+] Node public address: ")
    assert Web3.isAddress(node_addr) is True, Fore.RED + "[x] Address is invalid!"

    node_key = input("[+] Node private key: ")
    try:
        node_key = int(node_key, 16)
    except:
        print(Fore.RED + "[x] Private key is invalid!")
        exit()

    contract_addr = input("[+] Contract address: ")
    assert Web3.isAddress(contract_addr) is True, Fore.RED + "[x] Address is invalid!"

    contract_instance = w3.eth.contract(address=contract_addr, abi=abi)

    # authenticate node
    token = Web3.toInt(
        Web3.solidityKeccak(
            ["uint256", "address", "uint256"], [int(time.time()), node_addr, node_key]
        )
    )
    msg_hash = Web3.toInt(
        Web3.solidityKeccak(["uint256", "address"], [token, node_addr])
    )
    r_auth, s_auth = generate_signature(msg_hash, node_key)
    try:
        tx_hash = contract_instance.functions.BCTrustV2_Auth(
            token, r_auth, s_auth
        ).transact({"from": node_addr, "to": contract_addr})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(Fore.GREEN + "[+] Authentication Success!" + Style.RESET_ALL)
    except:
        print(Fore.RED + "[x] Authentication failed!" + Style.RESET_ALL)
        exit()

    # register node
    group_id = contract_instance.functions.membersGrpId(node_addr).call()
    node_id = contract_instance.functions.membersId(node_addr).call()
    node_data = {
        "pub_addr": node_addr,
        "node_id": node_id,
        "group_id": group_id,
        "token": token,
    }

    # main loop
    while True:
        print(Style.RESET_ALL, end="")
        print("-" * 50)
        print("[+] Select an option:")
        print("[1] Add node")
        print("[2] Send a message")
        print("[3] Read messages")
        print("[q] Quit")
        try:
            selection = input("[>] ").strip()
        except KeyboardInterrupt:
            print(Fore.YELLOW + "[!] Exiting..." + Style.RESET_ALL)
            break

        try:
            selection = int(selection)
        except:
            if selection == "q":
                print(Fore.YELLOW + "[!] Exiting...")
                break
            else:
                print(Fore.RED + "[x] Invalid selection!")
                continue

        if selection == 1:
            if node_data["group_id"] != 0:
                print(Fore.YELLOW + "[!] Node already registered!")
                continue

            while True:
                try:
                    category = int(input("[+] Node type (0: master, 1: slave): "))
                except:
                    print(Fore.RED + "[x] Invalid selection!" + Style.RESET_ALL)
                    continue

                if category in [0, 1]:
                    break
                else:
                    print(Fore.YELLOW + "[!] Invalid selection!" + Style.RESET_ALL)
            while True:
                try:
                    group_id = int(input("[+] Group ID (hex): "), 16)
                except:
                    print(Fore.YELLOW + "[!] Invalid group ID!" + Style.RESET_ALL)
                    continue

                if group_id > 0:
                    break
                else:
                    print(
                        Fore.YELLOW
                        + "[!] Group ID must be greater than 0!"
                        + Style.RESET_ALL
                    )
            while True:
                try:
                    node_id = int(input("[+] Node ID (hex): "), 16)
                except:
                    print(Fore.YELLOW + "[!] Invalid node ID!" + Style.RESET_ALL)
                    continue

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
                try:
                    r = int(input("[+] Ticket (int r): "))
                    s = int(input("[+] Ticket (int s): "))
                except:
                    print(Fore.YELLOW + "[!] Invalid ticket!" + Style.RESET_ALL)
                    continue

            try:
                tx_hash = contract_instance.functions.BCTrustV2_AddNode(
                    node_data["token"], category, group_id, node_id, r, s
                ).transact(
                    {
                        "from": node_addr,
                        "to": contract_addr,
                    }
                )
                w3.eth.wait_for_transaction_receipt(tx_hash)
                print(Fore.GREEN + f"[+] Add node successfully!")
                node_data["node_id"] = node_id
                node_data["group_id"] = group_id
            except:
                print(Fore.RED + "[x] Association failed!")
        elif selection == 2:
            if node_data["node_id"] == 0:
                print(Fore.YELLOW + "[!] Node not registered!")
                continue

            sender_id = node_data["node_id"]
            try:
                receiver_id = int(input("[+] Receiver ID (hex): "), 16)
            except:
                print(Fore.YELLOW + "[!] Invalid receiver ID!" + Style.RESET_ALL)
                continue

            try:
                message = input("[+] Message: ")
            except KeyboardInterrupt:
                print(Fore.YELLOW + "[!] Exiting..." + Style.RESET_ALL)
                break

            try:
                tx_hash = contract_instance.functions.BCTrustV2_Send(
                    node_data["token"], sender_id, receiver_id, message
                ).transact(
                    {
                        "from": node_addr,
                        "to": contract_addr,
                    }
                )
                w3.eth.wait_for_transaction_receipt(tx_hash)
                print(Fore.GREEN + "[+] Message sending succeeded!")
            except:
                print(Fore.RED + "[x] Message sending failed!")
        elif selection == 3:
            if node_data["node_id"] == 0:
                print(Fore.YELLOW + "[!] Node not registered!")
                continue

            node_id = node_data["node_id"]
            node_token = node_data["token"]
            try:
                # this call requires the 'from' and 'to' parameters
                # otherwise, the OnlyConcernedObject modifier in Solidity would fail!
                message = contract_instance.functions.BCTrustV2_ReadMSG(
                    node_data["token"], node_id
                ).call({"from": node_addr, "to": contract_addr})
            except:
                print(Fore.RED + "[x] Message reading failed!")
                print(node_id)
                print(node_token)
                continue

            if len(message) > 0:
                print(Fore.GREEN + f"[msg] {message}")
            else:
                print(Fore.YELLOW + "[!] No new messages!")
            try:
                tx_hash = contract_instance.functions.BCTrustV2_ClearMSG(
                    node_data["token"], node_id
                ).transact(
                    {
                        "from": node_addr,
                        "to": contract_addr,
                    }
                )
            except:
                pass

    print(Fore.YELLOW + "[!] Deauthenticating...")
    tx_hash = contract_instance.functions.BCTrustV2_Deauth(node_data["token"]).transact(
        {"from": node_addr, "to": contract_addr}
    )
    w3.eth.wait_for_transaction_receipt(tx_hash)

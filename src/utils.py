import json
import os
from web3 import Web3


# TODO: Implement parse_args
def init_contract():
    # connect to the provider
    w3 = Web3(Web3.HTTPProvider("http://192.168.100.3:7545"))

    # get the compiled contract
    with open(os.path.join("contracts", "abi.json")) as f:
        abi = json.load(f)

    with open(os.path.join("contracts", "bytecode.txt")) as f:
        bytecode = f.read()

    return w3, abi, bytecode
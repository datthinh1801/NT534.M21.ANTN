import json
import os
from web3 import Web3


# connect to the provider
w3 = Web3(Web3.HTTPProvider('http://192.168.100.3:7545'))

# get the contract
address = '0x73653581276829147710eD0e9c2EB6F6e6A64e60'
with open(os.path.join('contracts', 'abi.json')) as f:
    abi = json.load(f)

contract = web3.eth.contract(address=address, abi=abi)
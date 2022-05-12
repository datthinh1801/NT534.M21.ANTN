from utils import *


if __name__ == "__main__":
    w3, abi, bytecode = init_contract()

    w3.eth.default_account = w3.eth.accounts[0]
    bctrust = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = bctrust.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contract = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi,
    )
    print(tx_receipt.contractAddress)

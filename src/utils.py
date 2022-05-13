import json
import os
from argparse import ArgumentParser
from web3 import Web3


def parse_arguments():
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host address"
    )
    argument_parser.add_argument("--port", type=int, default=8545, help="Port number")
    return argument_parser.parse_args()


def init_contract():
    args = parse_arguments()
    # connect to the provider
    w3 = Web3(Web3.HTTPProvider(f"http://{args.host}:{args.port}"))

    # get the compiled contract
    with open(os.path.join("contracts", "abi.json")) as f:
        abi = json.load(f)

    with open(os.path.join("contracts", "bytecode.txt")) as f:
        bytecode = f.read()

    return w3, abi, bytecode

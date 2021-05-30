import typing as t

import os
import json

script_dir = os.path.dirname(__file__)


def load_lido_abi(path: str) -> t.List[t.Dict]:
    """Load an appropriate ABI file for Lido"""
    return json.load(open(path))


def get_default_lido_abi_path(chain_name: str) -> str:
    if chain_name == "mainnet":
        return os.path.join(script_dir, "abi/mainnet/Lido.json")
    elif chain_name == "goerli":
        return os.path.join(script_dir, "abi/goerli/Lido.json")
    else:
        raise Exception("Unable to load Lido ABI for network")


def load_operators_abi(path: str) -> t.List[t.Dict]:
    """Load an appropriate ABI file for Node Operators"""
    return json.load(open(path))


def get_default_operators_abi_path(chain_name: str) -> str:
    if chain_name == "mainnet":
        return os.path.join(script_dir, "abi/mainnet/NodeOperatorsRegistry.json")
    elif chain_name == "goerli":
        return os.path.join(script_dir, "abi/goerli/NodeOperatorsRegistry.json")
    else:
        raise Exception("Unable to load NodeOperatorsRegistry ABI for network")
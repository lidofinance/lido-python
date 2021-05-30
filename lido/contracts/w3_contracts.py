import typing as t

from lido.constants.contract_addresses import (
    get_default_lido_address,
)
from lido.contracts.abi_loader import load_lido_abi, load_operators_abi


def get_lido_contract(w3, address: str, path: str):
    """Load Lido web3 contract object"""
    return w3.eth.contract(address=address, abi=load_lido_abi(path=path))


def get_nos_contract(w3, address: str, path: str):
    """Load Node Operator web3 contract object"""
    return w3.eth.contract(
        address, abi=load_operators_abi(path=path)
    )

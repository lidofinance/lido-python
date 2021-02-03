import typing as t

from web3.auto import w3
from lido.constants.contract_addresses import (
    get_lido_address,
    get_registry_address,
)
from lido.contracts.abi_loader import load_lido_abi, load_operators_abi


def get_lido_contract(address: t.Optional[str] = None, path: t.Optional[str] = None):
    """Load Lido web3 contract object"""
    return w3.eth.contract(address=get_lido_address(address=address), abi=load_lido_abi(path=path))


def get_nos_contract(address: t.Optional[str] = None, path: t.Optional[str] = None):
    """Load Node Operator web3 contract object"""
    return w3.eth.contract(
        address=get_registry_address(address=address), abi=load_operators_abi(path=path)
    )

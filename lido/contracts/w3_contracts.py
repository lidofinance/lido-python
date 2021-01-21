from web3.auto import w3
from lido.constants.contract_addresses import (
    get_lido_address,
    get_node_operators_address,
)
from lido.contracts.abi_loader import load_lido_abi, load_operators_abi


def get_lido_contract():
    """Load Lido web3 contract object"""
    return w3.eth.contract(address=get_lido_address(), abi=load_lido_abi())


def get_nos_contract():
    """Load Node Operator web3 contract object"""
    return w3.eth.contract(address=get_node_operators_address(), abi=load_operators_abi())

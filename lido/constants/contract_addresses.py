import typing as t

import os

from web3.auto import w3
from lido.constants.chains import chains

LIDO_ADDRESSES = {
    "mainnet": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
    "goerli": "0x1643E812aE58766192Cf7D2Cf9567dF2C37e9B7F",
}

NODE_OPS_ADDRESSES = {
    "mainnet": "0x55032650b14df07b85bF18A3a3eC8E0Af2e028d5",
    "goerli": "0x9D4AF1Ee19Dad8857db3a45B0374c81c8A1C6320",
}


def get_lido_address(address: t.Optional[str] = None) -> str:
    """Return an appropriate Lido address for current network"""

    if address:
        return address

    env = os.getenv("LIDO_ADDRESS")

    if env is not None:
        return env

    chain = w3.eth.chainId
    return LIDO_ADDRESSES[chains[chain]]


def get_registry_address(address: t.Optional[str] = None) -> str:
    """Return an appropriate Node Operator (registry) address for current network"""

    if address:
        return address

    env = os.getenv("REGISTRY_ADDRESS")

    if env is not None:
        return env

    chain = w3.eth.chainId
    return NODE_OPS_ADDRESSES[chains[chain]]

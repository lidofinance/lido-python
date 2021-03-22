import typing as t

import os

from web3.auto import w3
from lido.constants.chains import chains

LIDO_ADDRESSES = {
    "mainnet": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
    "goerli": "0x5feB011F04Ec47cA42E75F5AC2bea4C50A646054",
}

NODE_OPS_ADDRESSES = {
    "mainnet": "0x55032650b14df07b85bF18A3a3eC8E0Af2e028d5",
    "goerli": "0xc210F98F7BF724ad1ec14064137AbcE4403f7e4f",
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

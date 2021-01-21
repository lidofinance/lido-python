from web3.auto import w3
from lido.constants.chains import chains

LIDO_ADDRESSES = {
    "mainnet": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
    "goerli": "0xA5d26F68130c989ef3e063c9bdE33BC50a86629D",
}

NODE_OPS_ADDRESSES = {
    "mainnet": "0x55032650b14df07b85bF18A3a3eC8E0Af2e028d5",
    "goerli": "0xB1e7Fb9E9A71063ab552dDEE87Ea8C6eEc7F5c7A",
}


def get_lido_address():
    """Return an appropriate Lido address for current network"""
    chain = w3.eth.chainId
    return LIDO_ADDRESSES[chains[chain]]


def get_node_operators_address():
    """Return an appropriate Node Operator address for current network"""
    chain = w3.eth.chainId
    return NODE_OPS_ADDRESSES[chains[chain]]
from lido.constants.chains import chains

LIDO_ADDRESSES = {
    "mainnet": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
    "ropsten": "0xd40EefCFaB888C9159a61221def03bF77773FC19",
    "goerli": "0x1643E812aE58766192Cf7D2Cf9567dF2C37e9B7F",
}

NODE_OPS_ADDRESSES = {
    "mainnet": "0x55032650b14df07b85bF18A3a3eC8E0Af2e028d5",
    "ropsten": "0x32c6f34F3920E8c0074241619c02be2fB722a68d",
    "goerli": "0x9D4AF1Ee19Dad8857db3a45B0374c81c8A1C6320",
}


def get_default_lido_address(chain_id) -> str:
    """Return an appropriate Lido address for current network"""

    return LIDO_ADDRESSES[chains[chain_id]]


def get_default_registry_address(chain_name) -> str:
    """Return an appropriate Node Operator (registry) address for current network"""

    return NODE_OPS_ADDRESSES[chain_name]

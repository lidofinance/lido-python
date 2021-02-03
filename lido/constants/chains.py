from web3.auto import w3

# We are deployed on Goerli and Mainnet
chains = {1: "mainnet", 5: "goerli"}


def get_chain_name() -> str:
    """Return a readable network name for current network"""
    return chains[w3.eth.chainId]


def get_eth2_chain_name() -> str:
    """Return a readable network name for current network for eth2-deposit-cli library"""

    # Return Pyrmont for Goerli deployment
    if w3.eth.chainId == 5:
        return "pyrmont"

    return chains[w3.eth.chainId]

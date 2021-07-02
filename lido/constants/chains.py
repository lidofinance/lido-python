# We are deployed on Goerli and Mainnet
chains = {1: "mainnet", 5: "goerli"}


def get_chain_name(chain_id) -> str:
    """Return a readable network name for current network"""
    return chains[chain_id]


def get_eth2_chain_name(chain_id) -> str:
    """Return a readable network name for current network for eth2-deposit-cli library"""

    # Return Pyrmont for Goerli deployment
    if chain_id == 5:
        return "prater"

    return chains[chain_id]

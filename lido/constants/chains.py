# We are deployed on Mainnet, Goerli and Ropsten
chains = {1: "mainnet", 3: "ropsten", 5: "goerli"}


def get_chain_name(chain_id) -> str:
    """Return a readable network name for current network"""

    return chains[chain_id]


def get_eth2_chain_name(chain_id) -> str:
    """Return a readable network name for current network for eth2-deposit-cli library"""

    # Mainnet-Mainnet deployment
    if chain_id == 1:
        return "mainnet"

    # Goerli-Prater deployment
    if chain_id == 5:
        return "prater"

    # Ropsten-Mainnet deployment
    if chain_id == 3:
        return "mainnet"

import typing as t

from web3.auto import w3

# Inject middleware for geth if we are on Goerli
if w3.eth.chainId == 5:
    from web3.middleware import geth_poa_middleware

    w3.middleware_onion.inject(geth_poa_middleware, layer=0)


def get_data_actuality() -> t.Dict:
    return {
        "last_block": w3.eth.getBlock("latest")["number"],
        "last_blocktime": w3.eth.getBlock("latest")["timestamp"],
    }

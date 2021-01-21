from web3.auto import w3


def get_data_actuality():
    return {
        "last_block": w3.eth.getBlock("latest")["number"],
        "last_blocktime": w3.eth.getBlock("latest")["timestamp"],
    }

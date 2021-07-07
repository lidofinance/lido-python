import typing as t


def get_data_actuality(w3) -> t.Dict:
    return {
        "last_block": w3.eth.getBlock("latest")["number"],
        "last_blocktime": w3.eth.getBlock("latest")["timestamp"],
    }

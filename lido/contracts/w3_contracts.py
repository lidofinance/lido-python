from lido.contracts.abi_loader import load_contract_abi


def get_contract(w3, address: str, path: str):
    """Load web3 contract object"""
    return w3.eth.contract(address=address, abi=load_contract_abi(path=path))

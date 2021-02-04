import typing as t

import os
import json
from lido.constants.chains import get_chain_name

network = get_chain_name()
script_dir = os.path.dirname(__file__)


def load_lido_abi(path: t.Optional[str] = None) -> t.List[t.Dict]:
    """Load an appropriate ABI file for Lido"""

    if path:
        return json.load(open(path))

    env = os.getenv("lido_abi")

    if env is not None:
        return json.load(open(env))

    if network == "mainnet":
        return json.load(open(os.path.join(script_dir, "abi/mainnet/Lido.json")))
    elif network == "goerli":
        return json.load(open(os.path.join(script_dir, "abi/goerli/Lido.json")))
    else:
        raise Exception("Unable to load Lido ABI for network")


def load_operators_abi(path: t.Optional[str] = None) -> t.List[t.Dict]:
    """Load an appropriate ABI file for Node Operators"""

    if path:
        return json.load(open(path))

    env = os.getenv("REGISTRY_ABI")

    if env is not None:
        return json.load(open(env))

    if network == "mainnet":
        return json.load(open(os.path.join(script_dir, "abi/mainnet/NodeOperatorsRegistry.json")))
    elif network == "goerli":
        return json.load(open(os.path.join(script_dir, "abi/goerli/NodeOperatorsRegistry.json")))
    else:
        raise Exception("Unable to load NodeOperatorsRegistry ABI for network")

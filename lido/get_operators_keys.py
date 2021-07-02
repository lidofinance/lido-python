import typing as t
import logging

from lido.multicall import Call, Multicall
from lido.contracts.w3_contracts import get_contract

logger = logging.getLogger(__name__)


def get_operators_keys(
    w3,
    operators: t.List[t.Dict],
    registry_address: str,
    registry_abi_path: str,
    max_multicall: int,
) -> t.List[t.Dict]:
    """Get and add signing keys to node operators

    Example output:
    [{
        'id': 0,
        'active': True,
        'name': 'Staking Facilities',
        'rewardAddress': '0xdd4bc51496dc93a0c47008e820e0d80745476f22',
        'stakingLimit': 1000,
        'stoppedValidators': 0,
        'totalSigningKeys': 1000,
        'usedSigningKeys': 560,
        'keys': [{
            'index': 0,
            'key': b '\x81\xb4\xaea\xa8\x989i\x03\x89\x7f\x94\xbe\xa0\xe0b\xc3\xa6\x92^\xe9=0\xf4\xd4\xae\xe9;S;IU\x1a\xc37\xdax\xff*\xb0\xcf\xbb\n\xdb8\x0c\xad\x94',
            'depositSignature': b '\x96\xa8\x8f\x8e\x88>\x9f\xf6\xf3\x97Q\xa2\xcb\xfc\xa3\x94\x9fO\xa9j\xe9\x84D\xd0\x05\xb6\xea\x9f\xaa\xc0\xc3KR\xd5\x95\xf9B\x8d\x90\x1d\xdd\x815$\x83}\x86d\x01\xedL\xed=\x84\xe7\xe88\xa2e\x06\xae.\xf3\xbf\x0b\xf1\xb8\xd3\x8b+\xd7\xbd\xb6\xc1<_F\xb8H\xd0-\xdc\x11\x08d\x9e\x96\x07\xcfM/\xce\xcd\xd8\x07\xbb',
            'used': True
        }, ...]
    }, ...]
    """

    for op_i, op in enumerate(operators):
        total_keys = op["totalSigningKeys"]

        keys = []

        calls_list = []
        for i in range(total_keys):
            call = Call(
                w3,
                registry_address,
                [
                    "getSigningKey(uint256,uint256)(bytes,bytes,bool)",
                    op_i,
                    i,
                ],
                [[i, None]],
            )
            calls_list.append(call)
            if len(calls_list) >= max_multicall:
                logger.debug(f"{len(calls_list)=}")
                multi_call = Multicall(w3, calls_list)()
                calls_list = []
                keys.extend(multi_call.values())

        if calls_list:
            logger.debug(f"{len(calls_list)=}")
            multi_call = Multicall(w3, calls_list)()
            keys.extend(multi_call.values())

        function_abi = next(
            x
            for x in get_contract(w3, address=registry_address, path=registry_abi_path).abi
            if x["name"] == "getSigningKey"
        )
        signing_keys_keys = ["index"] + [x["name"] for x in function_abi["outputs"]]
        signing_keys_list = [
            dict(
                zip(
                    signing_keys_keys,
                    [i] + list(item),
                )
            )
            for i, item in enumerate(keys)
        ]

        operators[op_i]["keys"] = signing_keys_list

    return operators

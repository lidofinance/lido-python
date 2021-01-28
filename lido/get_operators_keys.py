import typing as t
import logging

from lido.multicall import Call, Multicall
from lido.constants.contract_addresses import get_registry_address
from lido.contracts.w3_contracts import get_nos_contract

logger = logging.getLogger(__name__)


def split(data, chunk_length):
    """Split data to chunks of length n"""
    for i in range(0, len(data), chunk_length):
        yield data[i : i + chunk_length]


def prepare_batches(keys_number):
    """Prepare batches of a supplied number range"""

    range_of_data = list(range(keys_number))
    batches = split(range_of_data, 500)
    return list(batches)


def get_operators_keys(
        operators,
        max_multicall: int = 100,
        registry_address: t.Optional[str] = None,
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

    address = registry_address or get_registry_address()

    for op_i, op in enumerate(operators):
        chunks = prepare_batches(op["totalSigningKeys"])

        keys = []
        for chunk in chunks:
            calls_list = []
            for i in chunk:
                call = Call(
                    address,
                    [
                        "getSigningKey(uint256,uint256)(bytes,bytes,bool)",
                        op_i,
                        i,
                    ],
                    [[i, None]],
                )
                calls_list.append(call)
                if len(calls_list) >= max_multicall:
                    logger.debug(f'{len(calls_list)=}')
                    multi_call = Multicall(calls_list)()
                    calls_list = []
                    keys.extend(multi_call.values())
                    break
            if calls_list:
                logger.debug(f'{len(calls_list)=}')
                multi_call = Multicall(calls_list)()
                keys.extend(multi_call.values())

        function_abi = next(x for x in get_nos_contract().abi if x["name"] == "getSigningKey")
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

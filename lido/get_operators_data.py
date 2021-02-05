import typing as t
import logging

from lido.multicall import Call, Multicall
from lido.constants.contract_addresses import get_registry_address
from lido.contracts.w3_contracts import get_nos_contract

logger = logging.getLogger(__name__)


def get_operators_data(
    registry_address: t.Optional[str] = None,
    registry_abi_path: t.Optional[str] = None,
) -> t.List[t.Dict]:
    """Fetch information for each node operator"""
    address = registry_address or get_registry_address()
    operators_n = Call(address, "getNodeOperatorsCount()(uint256)")()
    logger.debug(f'{operators_n=}')
    if operators_n == 0:
        logger.warning(f'no operators')  # fixme assert if not test env
        return []
    assert operators_n < 1_000_000, 'too big operators_n'

    calls = Multicall(
        [
            Call(
                address,
                [
                    "getNodeOperator(uint256,bool)(bool,string,address,uint64,uint64,uint64,uint64)",
                    i,
                    True,
                ],
                [[i, None]],
            )
            for i in range(operators_n)
        ]
    )()

    calls_list = list(calls.values())

    # Adding index as first data of operator
    calls_with_indeces = [[i] + list(item) for i, item in enumerate(calls_list)]

    # Getting function data from contract ABI
    function_abi = next(
        x
        for x in get_nos_contract(address=registry_address, path=registry_abi_path).abi
        if x["name"] == "getNodeOperator"
    )

    # Adding "id" and the rest of output name keys
    op_keys = ["id"] + [x["name"] for x in function_abi["outputs"]]
    operators = [dict(zip(op_keys, op)) for op in calls_with_indeces]

    return operators

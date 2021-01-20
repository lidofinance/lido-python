from lido_network_helpers.multicall import Call, Multicall
from lido_network_helpers.constants.contract_addresses import get_node_operators_address
from lido_network_helpers.contracts.w3_contracts import get_nos_contract


def get_operators_data():
    """Fetch information for each node operator"""

    address = get_node_operators_address()

    operators_n = Call(address, "getNodeOperatorsCount()(uint256)")()

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
    function_data = next(
        (x for x in get_nos_contract().abi if x["name"] == "getNodeOperator"), None
    )

    # Adding "id" and the rest of output name keys
    op_keys = ["id"] + [x["name"] for x in function_data["outputs"]]
    operators = [dict(zip(op_keys, op)) for op in calls_with_indeces]

    return operators

from lido_network_helpers.multicall import Call, Multicall
from lido_network_helpers.constants.contract_addresses import get_node_operators_address
from lido_network_helpers.contracts.w3_contracts import get_nos_contract


def split(data, chunk_length):
    """Split data to chunks of length n"""
    for i in range(0, len(data), chunk_length):
        yield data[i : i + chunk_length]


def prepare_batches(keys_number):
    """Prepare batches of a supplied number range"""

    range_of_data = list(range(keys_number))
    batches = split(range_of_data, 1000)
    return list(batches)


def get_operators_keys(operators):
    """Get and add signing keys to node operators"""

    address = get_node_operators_address()

    for op_i, op in enumerate(operators):
        chunks = prepare_batches(op["totalSigningKeys"])

        keys = []
        for chunk in chunks:

            calls = Multicall(
                [
                    Call(
                        address,
                        [
                            "getSigningKey(uint256,uint256)(bytes,bytes,bool)",
                            op_i,
                            i,
                        ],
                        [[i, None]],
                    )
                    for i in chunk
                ]
            )()

            for item in list(calls.values()):
                keys.append(item)

        function_data = next(
            (x for x in get_nos_contract().abi if x["name"] == "getSigningKey"), None
        )

        signing_keys_keys = ["index"] + [x["name"] for x in function_data["outputs"]]

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

from lido.multicall import Call, Multicall
from lido.constants.contract_addresses import get_lido_address
from lido.contracts.w3_contracts import get_lido_contract
from lido.utils.data_actuality import get_data_actuality

# Default functions to execute, this can be easily overridden
funcs_to_fetch = [
    "isStopped",
    "getTotalPooledEther",
    "getWithdrawalCredentials",
    "getFee",
    "getFeeDistribution",
    "getBeaconStat",
    "getBufferedEther",
]


def get_stats(funcs_to_fetch=funcs_to_fetch):
    """Fetch various constants from Lido for analytics and statistics"""

    address = get_lido_address()

    # Getting function data from contract ABI
    funcs_from_contract = [
        x
        for x in get_lido_contract().abi
        if x["type"] == "function" and x["name"] in funcs_to_fetch
    ]

    # Adding "multicall_outputs" with prepared input data for multicall
    for func_i, func in enumerate(funcs_from_contract):
        x = []
        for output in func["outputs"]:
            x.append(output["type"])
        funcs_from_contract[func_i]["multicall_outputs"] = ",".join(x)

    calls = Multicall(
        [
            Call(
                address,
                [
                    "%s()(%s)" % (item["name"], item["multicall_outputs"]),
                ],
                [[item["name"], None]],
            )
            for item in funcs_from_contract
        ]
    )()

    actuality_data = get_data_actuality()

    return {**actuality_data, **calls}

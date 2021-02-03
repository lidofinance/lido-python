import typing as t

from py_ecc.bls import G2ProofOfPossession as bls
from lido.eth2deposit.utils.ssz import (
    DepositMessage,
    compute_deposit_domain,
    compute_signing_root,
)
from lido.eth2deposit.settings import get_chain_setting
from lido.constants.chains import get_eth2_chain_name
from lido.contracts.w3_contracts import get_lido_contract

import concurrent


def validate_key(data: t.Dict) -> t.Optional[bool]:
    """Run signature validation on a key"""

    key = data["key"]
    withdrawal_credentials = data["withdrawal_credentials"]

    # Is this key already validated?
    if "valid_signature" in key.keys():
        return None

    pubkey = bytes.fromhex(key["key"]) if type(key["key"]) is str else key["key"]
    signature = (
        bytes.fromhex(key["depositSignature"])
        if type(key["depositSignature"]) is str
        else key["depositSignature"]
    )

    fork_version = get_chain_setting(get_eth2_chain_name()).GENESIS_FORK_VERSION
    domain = compute_deposit_domain(fork_version=fork_version)

    # Minimum staking requirement of 32 ETH per validator
    REQUIRED_DEPOSIT_ETH = 32
    ETH2GWEI = 10 ** 9
    amount = REQUIRED_DEPOSIT_ETH * ETH2GWEI

    deposit_message = DepositMessage(
        pubkey=pubkey,
        withdrawal_credentials=withdrawal_credentials,
        amount=amount,
    )

    signing_root = compute_signing_root(deposit_message, domain)

    return bls.Verify(pubkey, signing_root, signature)


def validate_keys_mono(
    operators: t.List[t.Dict],
    lido_address: t.Optional[str] = None,
    lido_abi_path: t.Optional[str] = None,
) -> t.List[t.Dict]:
    """
    This is an additional, single-process key validation function.
    Modifies the input! Adds "valid_signature" field to every key item.
    """

    # Prepare network vars
    lido = get_lido_contract(address=lido_address, path=lido_abi_path)
    withdrawal_credentials = bytes(lido.functions.getWithdrawalCredentials().call())

    for op_i, op in enumerate(operators):
        for key_i, key in enumerate(op["keys"]):
            # Is this key already validated?
            if "valid_signature" not in key.keys():
                operators[op_i]["keys"][key_i]["valid_signature"] = validate_key(
                    {"key": key, "withdrawal_credentials": withdrawal_credentials}
                )

    return operators


def validate_keys_multi(
    operators: t.List[t.Dict],
    lido_address: t.Optional[str] = None,
    lido_abi_path: t.Optional[str] = None,
) -> t.List[t.Dict]:
    """
    Main multi-process validation function.
    Modifies the input! Adds "valid_signature" field to every key item.
    It will spawn an appropriate process pool for the amount of threads on processor.
    """

    # Prepare network vars
    lido = get_lido_contract(address=lido_address, path=lido_abi_path)
    withdrawal_credentials = bytes(lido.functions.getWithdrawalCredentials().call())

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for op_i, op in enumerate(operators):

            # Pass {key,withdrawal_credentials} to overcome 1-arg limit of concurrency.map()
            arguments = [
                {"key": key, "withdrawal_credentials": withdrawal_credentials} for key in op["keys"]
            ]

            validate_key_results = executor.map(validate_key, arguments)

            for key_index, validate_key_result in enumerate(validate_key_results):
                # Is this key already validated?
                if validate_key_result is not None:
                    operators[op_i]["keys"][key_index]["valid_signature"] = validate_key_result

    return operators


def validate_key_list_multi(
    input: t.List[t.Dict],
    lido_address: t.Optional[str] = None,
    lido_abi_path: t.Optional[str] = None,
) -> t.List[t.Dict]:
    """
    Additional multi-process validation function.
    It returns invalid keys instead of the whole operator data like other functions.
    """

    # Prepare network
    lido = get_lido_contract(address=lido_address, path=lido_abi_path)
    withdrawal_credentials = bytes(lido.functions.getWithdrawalCredentials().call())

    invalid = []

    with concurrent.futures.ProcessPoolExecutor() as executor:

        # Pass {key,withdrawal_credentials} to overcome 1-arg limit of concurrency.map()
        arguments = [
            {"key": key, "withdrawal_credentials": withdrawal_credentials} for key in input
        ]

        validate_key_results = executor.map(validate_key, arguments)

        for key_index, validate_key_result in enumerate(validate_key_results):
            # Is this key already validated?
            if validate_key_result is not None and validate_key_result is False:
                invalid.append(input[key_index])

    return invalid

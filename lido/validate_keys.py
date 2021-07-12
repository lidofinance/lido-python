import typing as t

from py_ecc.bls import G2ProofOfPossession as bls
from lido.eth2deposit.utils.ssz import (
    DepositMessage,
    compute_deposit_domain,
    compute_signing_root,
)
from lido.eth2deposit.settings import get_chain_setting
from lido.constants.chains import get_chain_name, get_eth2_chain_name
from lido.constants.withdrawal_credentials import get_withdrawal_credentials
from lido.contracts.w3_contracts import get_contract

import concurrent


def gen_possible_withdrawal_credentials(live_withdrawal_credentials, chain_id):
    return list(
        set([live_withdrawal_credentials] + get_withdrawal_credentials(get_chain_name(chain_id)))
    )


def validate_key(data: t.Dict) -> t.Optional[bool]:
    """Run signature validation on a key"""

    key = data["key"]
    chain_id = data["chain_id"]
    live_withdrawal_credentials = data["live_withdrawal_credentials"]
    possible_withdrawal_credentials = data["possible_withdrawal_credentials"]
    strict = data["strict"]

    # Is this key already validated?
    if "valid_signature" in key.keys():
        return None

    pubkey = bytes.fromhex(key["key"]) if type(key["key"]) is str else key["key"]
    signature = (
        bytes.fromhex(key["depositSignature"])
        if type(key["depositSignature"]) is str
        else key["depositSignature"]
    )

    fork_version = get_chain_setting(get_eth2_chain_name(chain_id)).GENESIS_FORK_VERSION
    domain = compute_deposit_domain(fork_version=fork_version)

    # Minimum staking requirement of 32 ETH per validator
    REQUIRED_DEPOSIT_ETH = 32
    ETH2GWEI = 10 ** 9
    amount = REQUIRED_DEPOSIT_ETH * ETH2GWEI

    # If strict, not using any previous withdrawal credentials
    # Checking only actual live withdrawal credentials for unused keys
    if strict or ("used" in key and key["used"] is False):
        deposit_message = DepositMessage(
            pubkey=pubkey,
            withdrawal_credentials=live_withdrawal_credentials,
            amount=amount,
        )

        signing_root = compute_signing_root(deposit_message, domain)

        return bls.Verify(pubkey, signing_root, signature)

    # If a key has been used already or in loose mode, checking both new and any olds withdrawal creds
    for wc in possible_withdrawal_credentials:
        deposit_message = DepositMessage(
            pubkey=pubkey,
            withdrawal_credentials=wc,
            amount=amount,
        )

        signing_root = compute_signing_root(deposit_message, domain)

        verified = bls.Verify(pubkey, signing_root, signature)

        # Early exit when any key succeeds validation
        if verified is True:
            return True

    # Exit with False if none of the withdrawal creds combination were valid
    return False


def validate_keys_mono(
    w3, operators: t.List[t.Dict], lido_address: str, lido_abi_path: str, strict: bool
) -> t.List[t.Dict]:
    """
    This is an additional, single-process key validation function.
    Modifies the input! Adds "valid_signature" field to every key item.
    """

    # Prepare network vars
    lido = get_contract(w3, address=lido_address, path=lido_abi_path)
    chain_id = w3.eth.chainId
    live_withdrawal_credentials = lido.functions.getWithdrawalCredentials().call()

    possible_withdrawal_credentials = gen_possible_withdrawal_credentials(
        live_withdrawal_credentials, chain_id
    )

    for op_i, op in enumerate(operators):
        for key_i, key in enumerate(op["keys"]):
            # Is this key already validated?
            if "valid_signature" not in key.keys():
                operators[op_i]["keys"][key_i]["valid_signature"] = validate_key(
                    {
                        "chain_id": chain_id,
                        "key": key,
                        "live_withdrawal_credentials": live_withdrawal_credentials,
                        "possible_withdrawal_credentials": possible_withdrawal_credentials,
                        "strict": strict,
                    }
                )

    return operators


def validate_keys_multi(
    w3, operators: t.List[t.Dict], lido_address: str, lido_abi_path: str, strict: bool
) -> t.List[t.Dict]:
    """
    Main multi-process validation function.
    Modifies the input! Adds "valid_signature" field to every key item.
    It will spawn an appropriate process pool for the amount of threads on processor.
    """

    # Prepare network vars
    lido = get_contract(w3, address=lido_address, path=lido_abi_path)
    chain_id = w3.eth.chainId
    live_withdrawal_credentials = lido.functions.getWithdrawalCredentials().call()

    possible_withdrawal_credentials = gen_possible_withdrawal_credentials(
        live_withdrawal_credentials, chain_id
    )

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for op_i, op in enumerate(operators):

            # Pass {} to overcome 1-arg limit of concurrency.map()
            arguments = [
                {
                    "chain_id": chain_id,
                    "key": key,
                    "live_withdrawal_credentials": live_withdrawal_credentials,
                    "possible_withdrawal_credentials": possible_withdrawal_credentials,
                    "strict": strict,
                }
                for key in op["keys"]
            ]

            validate_key_results = executor.map(validate_key, arguments)

            for key_index, validate_key_result in enumerate(validate_key_results):
                # Is this key already validated?
                if validate_key_result is not None:
                    operators[op_i]["keys"][key_index]["valid_signature"] = validate_key_result

    return operators


def validate_key_list_multi(
    w3, input: t.List[t.Dict], lido_address: str, lido_abi_path: str, strict: bool
) -> t.List[t.Dict]:
    """
    Additional multi-process validation function.
    It returns invalid keys instead of the whole operator data like other functions.
    """

    # Prepare network
    lido = get_contract(w3, address=lido_address, path=lido_abi_path)
    chain_id = w3.eth.chainId
    live_withdrawal_credentials = lido.functions.getWithdrawalCredentials().call()
    possible_withdrawal_credentials = gen_possible_withdrawal_credentials(
        live_withdrawal_credentials, chain_id
    )

    invalid = []

    with concurrent.futures.ProcessPoolExecutor() as executor:

        # Pass {} to overcome 1-arg limit of concurrency.map()
        arguments = [
            {
                "chain_id": chain_id,
                "key": key,
                "live_withdrawal_credentials": live_withdrawal_credentials,
                "possible_withdrawal_credentials": possible_withdrawal_credentials,
                "strict": strict,
            }
            for key in input
        ]

        validate_key_results = executor.map(validate_key, arguments)

        for key_index, validate_key_result in enumerate(validate_key_results):
            # Is this key already validated?
            if validate_key_result is not None and validate_key_result is False:
                invalid.append(input[key_index])

    return invalid

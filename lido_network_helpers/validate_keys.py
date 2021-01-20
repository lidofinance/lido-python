from py_ecc.bls import G2ProofOfPossession as bls
from lido_network_helpers.eth2deposit.utils.ssz import (
    DepositMessage,
    compute_deposit_domain,
    compute_signing_root,
)
from lido_network_helpers.eth2deposit.settings import get_chain_setting
from lido_network_helpers.constants.chains import get_eth2_chain_name
from lido_network_helpers.contracts.w3_contracts import get_lido_contract

import concurrent

# Prepare network
lido = get_lido_contract()
withdrawal_credentials = bytes(lido.functions.getWithdrawalCredentials().call())
fork_version = get_chain_setting(get_eth2_chain_name()).GENESIS_FORK_VERSION
domain = compute_deposit_domain(fork_version=fork_version)


def validate_key(key):
    """Run signature validation on a key"""

    pubkey = key["key"]
    signature = key["depositSignature"]

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


def validate_keys_mono(operators):
    """This is an additional, single-process key validation function"""

    for op_i, op in enumerate(operators):
        for key_i, key in enumerate(op["keys"]):
            operators[op_i]["keys"][key_i]["valid_signature"] = validate_key(key)

    return operators


def validate_keys_multi(operators):
    """
    Main multi-process validation function.
    It will spawn an appropriate process pool for the amount of threads on processor.

    --- WARNING ---
    Required for this to work:

    Main function and

    if __name__ == "__main__":
        main()

    in top level scope.

    --- WARNING ---
    """

    with concurrent.futures.ProcessPoolExecutor() as executor:

        for op_i, op in enumerate(operators):

            results = executor.map(validate_key, op["keys"])

            for result_i, result in enumerate(results):
                operators[op_i]["keys"][result_i]["valid_signature"] = result

    return operators

import logging
import time

from web3.auto import w3
from lido import Lido


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)8s %(asctime)s <daemon> %(message)s')

    start_time = time.time()

    if w3.eth.chainId == 5:
        from web3.middleware import geth_poa_middleware
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    lido = Lido(w3)

    operators_data = lido.get_operators_data()
    print("loaded operators data", time.time() - start_time)

    start_time2 = time.time()
    operators_with_keys = lido.get_operators_keys(operators_data)
    print("loaded operators keys", time.time() - start_time2)

    print("NETWORK OPERATIONS TIME", time.time() - start_time)

    start_time3 = time.time()
    operators_with_validated_keys = lido.validate_keys_multi(operators_with_keys)
    print("validated keys", time.time() - start_time3)

    start_time4 = time.time()
    operators_with_checked_duplicates = lido.find_duplicates(operators_with_validated_keys)
    print("found duplicates", time.time() - start_time4)

    print("finished script for", len(operators_with_checked_duplicates), "ops")
    print("TOTAL EXECUTION TIME", time.time() - start_time)

    """
    Code above would be equivalent to

    from lido import fetch_and_validate
    fetch_and_validate()

    if you need all validation functions.

    """

    start_time5 = time.time()
    stats = lido.get_stats()
    print("fetched stats", time.time() - start_time5)
    print(stats)


if __name__ == "__main__":
    main()

import time
from lido_network_helpers import (
    get_operators_data,
    get_operators_keys,
    validate_keys_multi,
    find_duplicates,
)


def main():
    start_time = time.time()
    operators_data = get_operators_data()
    print("loaded operators data", time.time() - start_time)

    start_time2 = time.time()
    operators_with_keys = get_operators_keys(operators_data)
    print("loaded operators keys", time.time() - start_time2)

    print("NETWORK OPERATIONS TIME", time.time() - start_time)

    start_time3 = time.time()
    operators_with_validated_keys = validate_keys_multi(operators_with_keys)
    print("validated keys", time.time() - start_time3)

    start_time4 = time.time()
    operators_with_checked_duplicates = find_duplicates(operators_with_validated_keys)
    print("found duplicates", time.time() - start_time4)

    print("finished script for", len(operators_with_checked_duplicates), "ops")
    print("TOTAL EXECUTION TIME", time.time() - start_time)


if __name__ == "__main__":
    main()

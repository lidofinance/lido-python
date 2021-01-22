from lido import (
    get_operators_data,
    get_operators_keys,
    validate_keys_multi,
    find_duplicates,
)


def fetch_and_validate():
    return find_duplicates(validate_keys_multi(get_operators_keys(get_operators_data())))

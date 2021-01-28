import typing as t

from lido import (
    get_operators_data,
    get_operators_keys,
    validate_keys_multi,
    find_duplicates,
)


def fetch_and_validate(registry_address: t.Optional[str] = None, max_multicall: int = 100) -> t.List[t.Dict]:
    """ fetches all operator keys, and run keys validations nad duplication checks

    check fields:
     - operators[op_i]["keys"][key_i]["duplicate"]
     - operators[op_i]["keys"][key_i]["duplicates"]
     - operators[op_i]["keys"][key_i]["valid_signature"]
    """
    operator_keys = get_operators_keys(get_operators_data(registry_address=registry_address),
                                       max_multicall=max_multicall)
    result = find_duplicates(validate_keys_multi(operator_keys))
    return result

import typing as t

from lido import (
    get_operators_data,
    get_operators_keys,
    validate_keys_multi,
    find_duplicates,
)


def fetch_and_validate(
    max_multicall: t.Optional[int] = None,
    lido_address: t.Optional[str] = None,
    lido_abi_path: t.Optional[str] = None,
    registry_address: t.Optional[str] = None,
    registry_abi_path: t.Optional[str] = None,
) -> t.List[t.Dict]:
    """fetches all operator keys, and run keys validations and duplication checks

    check fields:
     - operators[op_i]["keys"][key_i]["duplicate"]
     - operators[op_i]["keys"][key_i]["duplicates"]
     - operators[op_i]["keys"][key_i]["valid_signature"]
    """

    operators_data = get_operators_data(
        registry_address=registry_address, registry_abi_path=registry_abi_path
    )

    data_with_keys = get_operators_keys(
        operators=operators_data,
        max_multicall=max_multicall,
        registry_address=registry_address,
        registry_abi_path=registry_abi_path,
    )

    data_validated_keys = validate_keys_multi(
        operators=data_with_keys, lido_address=lido_address, lido_abi_path=lido_abi_path
    )

    data_found_duplicates = find_duplicates(operators=data_validated_keys)

    return data_found_duplicates

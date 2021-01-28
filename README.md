# Lido

This library consolidates various functions to efficiently load network data for Lido, validate node operator keys and find key duplicates.

## Installation

This library is available on PyPi:

`pip install lido`

## Main Features

### Multicall Function Calls

Instead of making network requests one-by-one, this library combines many requests into one RPC call. It uses [banteg/multicall.py](https://github.com/banteg/multicall.py), a Python wrapper for [makerdao/multicall](https://github.com/makerdao/multicall).

### Multiprocess Signature Validations

When using `validate_keys_multi()`, this library spreads processing of key signature validations to all system cores.

### Automatic Testnet / Mainnet Switching

Depending on the supplied WEB3_PROVIDER_URI, a correct network will be used. Even an appropriate ABI will be loaded for the chain automatically.

## Helpers Provided

- get_operators_data() -> operator_data - load node operator data

- get_operators_keys(operator_data) -> operator_data - fetches and adds keys to operator_data
- validate_keys_mono(operator_data) -> operator_data - validates keys in single process and adds validation results to operator_data
- validate_keys_multi(operator_data) -> operator_data - validates keys in multiple processes and adds validation results to operator_data, requires a main function (see example)
- validate_key([[key,depositSignature]]) -> Boolean - low-level validation function
- find_duplicates(operator_data) -> operator_data - finds duplicate keys and adds results to operator_data

- fetch_and_validate() -> operator_data - combines fetching operator data and running all validations on it - useful when you would be running all validations on data anyway

- get_stats() -> stats - fetches various constants from Lido contract, but you can even pass a list of functions to fetch eg get_stats([isStopped])

You can mix and match these functions, but make sure to use get_operators_data() first.

## Notes

1. Signature validation will be skipped if its results are already present in operator_data. This way you can safely load validation results from cache and add `["valid_signature"] = Boolean` to already checked keys.

## How to Use

Use a RPC provider url as an environment variable and run your script:

`WEB3_PROVIDER_URI=https://eth-mainnet.provider.xx example.py`

See `example.py` for a complete example, make sure to use a main function and a script entry point check when using validate_keys_multi() or fetch_and_validate().

## Options

If you are testing a new deployment of Lido, these environment variables can override addresses and ABIs:

- LIDO_ADDRESS
- REGISTRY_ADDRESS
- LIDO_ABI (the file-path to the contract's ABI)
- REGISTRY_ABI (the file-path to the contract's ABI)

`WEB3_PROVIDER_URI=https://eth-mainnet.provider.xx LIDO_ADDRESS=XXX REGISTRY_ADDRESS=XXX LIDO_ABI=xxx.json REGISTRY_ABI=xxx.json example.py`

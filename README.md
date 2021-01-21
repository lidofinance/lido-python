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
- validate_keys_multi(operator_data) -> operator_data - validates keys in multiple processes and adds validation results to operator_data
- find_duplicates(operator_data) -> operator_data - finds duplicate keys and adds results to operator_data

You can mix and match these functions, but make sure to use get_operators_data() first.

## How to Use

Use a RPC provider url as an environment variable and run your script:

`WEB3_PROVIDER_URI=https://eth-mainnet.provider.xx example.py`

See `example.py` for a complete example.

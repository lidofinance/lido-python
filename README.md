# Lido

This library consolidates various functions to efficiently load network data for Lido, validate node operator keys and find key duplicates.

## Installation

This library is available on PyPi:

`pip install lido`

## Quickstart

```
from web3 import Web3
from lido import Lido
w3 = Web3(...)
lido = Lido(w3)
operators = lido.fetch_and_validate()
```

## Main Features

### Multicall Function Calls

Instead of making network requests one-by-one, this library combines many requests into one RPC call. It uses [banteg/multicall.py](https://github.com/banteg/multicall.py), a Python wrapper for [makerdao/multicall](https://github.com/makerdao/multicall).

### Multiprocess Signature Validations

When using `validate_keys_multi()`, this library spreads processing of key signature validations to all system cores.

### Automatic Testnet / Mainnet Switching

Depending on which network is configured in web3 object, a set of contracts will be used. Even an appropriate ABI will be loaded for the chain automatically.

## Helpers Provided

- lido.get_operators_data() -> operator_data - load node operator data

- lido.get_operators_keys(operator_data) -> operator_data - fetches and adds keys to operator_data
- lido.validate_keys_mono(operator_data, strict = False) -> operator_data - validates keys in single process and adds validation results to operator_data
- lido.validate_keys_multi(operator_data, strict = False) -> operator_data - validates keys in multiple processes and adds validation results to operator_data, requires a main function (see example)
- lido.validate_key_list_multi(operator_data, strict = False) -> [] - same as validate_keys_multi(), but returns a list of invalid keys
- lido.validate_key(chain_id, key, withdrawal_credentials) -> Boolean - low-level validation function, doesn't check for correct
  chain_id and withdrawal_credentials for a Lido deployment. For most use-cases use validate_keys_multi or validate_key_list_multi instead
- lido.find_duplicates(operator_data) -> operator_data - finds duplicate keys and adds results to operator_data

- lido.fetch_and_validate() -> operator_data - combines fetching operator data and running all validations on it - useful when you would be running all validations on data anyway

- lido.get_stats() -> stats - fetches various constants from Lido contract, but you can even pass a list of functions to fetch eg get_stats(["isStopped"])

You can mix and match these functions, but make sure to use get_operators_data() first.

## Notes

1. Signature validation will be skipped if its results are already present in operator_data. This way you can safely load validation results from cache and add `["valid_signature"] = Boolean` to already checked keys.

2. Signature validation functions are accounting for previous withdrawal credentials by default. However, if you are building a fresh key validator it is vitally important to enable strict mode by setting strict argument of the functions to `True`. This way new keys with old withdrawal credentials won't pass validation.

## Running an example script

The example script uses web3.auto, so use a RPC provider url as an environment variable to run it:

`WEB3_PROVIDER_URI=https://eth-mainnet.provider.xx example.py`

See `example.py` for a complete example, make sure to use a main function and a script entry point check when using validate_keys_multi() or fetch_and_validate().

## Options

If you are testing a new deployment of Lido, you can override addresses and ABIs with constructor of Lido object. Also you can configure the maximum number of calls agregated to one multicall:

```
lido = Lido(
    w3,
    lido_address=LIDO_ADDRESS,
    registry_address=REGISTRY_ADDRESS,
    lido_abi_path=LIDO_ABI, # the file-path to the contract's ABI
    registry_abi_path=REGISTRY_ABI, # the file-path to the contract's ABI
    max_multicall=MAX_MULTICALL)
```

from lido.get_stats import get_stats
from lido.find_duplicates import find_duplicates
from lido.validate_keys import validate_keys_mono, validate_keys_multi
from lido.get_operators_keys import get_operators_keys
import typing as t
from lido.contracts.abi_loader import get_default_lido_abi_path, get_default_operators_abi_path
from lido import get_operators_data
from lido.constants.chains import get_chain_name
from lido.constants.contract_addresses import get_default_lido_address, get_default_registry_address

multicall_default_batch = 300

class Lido:
    def __init__(
        self, 
        w3,
        lido_address: t.Optional[str] = None,
        registry_address: t.Optional[str] = None,
        lido_abi_path: t.Optional[str] = None,
        registry_abi_path: t.Optional[str] = None,
        max_multicall: t.Optional[int] = multicall_default_batch,
    ) -> None:
        self.w3 = w3
        self.chain_id = w3.eth.chainId

        # Check if PoA middleware is injected if we are on Goerli
        if self.chain_id == 5:
            from web3.middleware import geth_poa_middleware
            # Checking by value b/c we don't know the key
            if geth_poa_middleware not in self.w3.middleware_onion:
                raise ValueError("Geth PoA middleware is not injected into Web3 middleware onion")

        self.chain_name = get_chain_name(self.chain_id)
        self.registry_address = registry_address or get_default_registry_address(self.chain_name)
        self.registry_abi_path = registry_abi_path or get_default_operators_abi_path(self.chain_name)
        self.lido_address = lido_address or get_default_lido_address(self.chain_id)
        self.lido_abi_path = lido_abi_path or get_default_lido_abi_path(self.chain_name)
        self.max_multicall = max_multicall

    def get_operators_data(self):
        return get_operators_data(self.w3, self.registry_address, self.registry_abi_path)

    def get_operators_keys(self, operators_data):
        return get_operators_keys(self.w3, operators_data, self.registry_address, self.registry_abi_path, self.max_multicall)

    def validate_keys_multi(self, operators_with_keys):
        return validate_keys_multi(self.w3, operators_with_keys, self.lido_address, self.lido_abi_path)

    def validate_keys_mono(self, operators_with_keys):
        return validate_keys_mono(self.w3, operators_with_keys, self.lido_address, self.lido_abi_path)

    def find_duplicates(self, operators_with_validated_keys):
        return find_duplicates(operators_with_validated_keys)

    def fetch_and_validate(self):
        """fetches all operator keys, and run keys validations and duplication checks

        check fields:
        - operators[op_i]["keys"][key_i]["duplicate"]
        - operators[op_i]["keys"][key_i]["duplicates"]
        - operators[op_i]["keys"][key_i]["valid_signature"]
        """

        operators_data = self.get_operators_data()

        data_with_keys = self.get_operators_keys(operators_data)

        data_validated_keys = self.validate_keys_multi(data_with_keys)

        data_found_duplicates = self.find_duplicates(data_validated_keys)

        return data_found_duplicates

    def get_stats(self):
        return get_stats(self.w3, lido_address=self.lido_address, lido_abi_path=self.lido_abi_path)
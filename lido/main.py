from lido.get_stats import get_stats
from lido.find_duplicates import find_duplicates, spot_duplicates
from lido.validate_keys import (
    validate_key_list_multi,
    validate_keys_mono,
    validate_keys_multi,
    validate_key,
)
from lido.get_operators_keys import get_operators_keys
import typing as t
from lido.contracts.abi_loader import get_default_lido_abi_path, get_default_operators_abi_path
from lido import get_operators_data
from lido.constants.chains import get_chain_name
from lido.constants.contract_addresses import get_default_lido_address, get_default_registry_address
from lido.contracts.w3_contracts import get_contract

multicall_default_batch = 300


class Lido:
    def __init__(
        self,
        w3,
        lido_address: t.Optional[str] = None,
        registry_address: t.Optional[str] = None,
        lido_abi_path: t.Optional[str] = None,
        registry_abi_path: t.Optional[str] = None,
        max_multicall: t.Optional[int] = None,
    ) -> None:
        self.w3 = w3
        self.chain_id = w3.eth.chainId

        # Check if PoA middleware is injected if we are on Goerli
        if self.chain_id == 5:
            from web3.middleware import geth_poa_middleware

            # Checking by value b/c we don't know the key
            if geth_poa_middleware not in self.w3.middleware_onion:
                raise ValueError("PoA middleware isn't injected into Web3 middleware onion")

        self.chain_name = get_chain_name(self.chain_id)
        self.registry_address = registry_address or get_default_registry_address(self.chain_name)
        self.registry_abi_path = registry_abi_path or get_default_operators_abi_path(
            self.chain_name
        )
        self.lido_address = lido_address or get_default_lido_address(self.chain_id)
        self.lido_abi_path = lido_abi_path or get_default_lido_abi_path(self.chain_name)
        self.max_multicall = max_multicall or multicall_default_batch

    def get_operators_data(self):
        return get_operators_data(self.w3, self.registry_address, self.registry_abi_path)

    def get_operators_keys(self, operators_data):
        return get_operators_keys(
            self.w3,
            operators_data,
            self.registry_address,
            self.registry_abi_path,
            self.max_multicall,
        )

    def validate_keys_multi(self, operators_with_keys, strict=False):
        return validate_keys_multi(
            self.w3, operators_with_keys, self.lido_address, self.lido_abi_path, strict
        )

    def validate_keys_mono(self, operators_with_keys, strict=False):
        return validate_keys_mono(
            self.w3, operators_with_keys, self.lido_address, self.lido_abi_path, strict
        )

    def validate_key_list_multi(self, operators_with_keys, strict=False):
        return validate_key_list_multi(
            self.w3, operators_with_keys, self.lido_address, self.lido_abi_path, strict
        )

    @staticmethod
    def find_duplicates(operators_with_validated_keys):
        return find_duplicates(operators_with_validated_keys)

    @staticmethod
    def spot_duplicates(operators, key, original_op=None):
        return spot_duplicates(operators, key, original_op)

    @staticmethod
    def validate_key(chain_id, key, withdrawal_credentials):
        """
        WARNING:
        This is a lower-level validation function without checks for correct
        chain_id and withdrawal_credentials for a Lido deployment.
        This is required for correct multiprocess operation.
        For most use-cases don't use it directly, use validate_keys_multi or
        validate_key_list_multi instead.
        """
        return validate_key(
            {"chain_id": chain_id, "key": key, "withdrawal_credentials": withdrawal_credentials}
        )

    def fetch_and_validate(self):
        operators_data = self.get_operators_data()

        data_with_keys = self.get_operators_keys(operators_data)

        data_validated_keys = self.validate_keys_multi(data_with_keys)

        data_found_duplicates = self.find_duplicates(data_validated_keys)

        return data_found_duplicates

    def get_stats(self, funcs_to_fetch=None):
        if funcs_to_fetch is None:
            # Default functions to execute, this can be easily overridden
            funcs_to_fetch = [
                "isStopped",
                "getTotalPooledEther",
                "getWithdrawalCredentials",
                "getFee",
                "getFeeDistribution",
                "getBeaconStat",
                "getBufferedEther",
            ]

        return get_stats(
            self.w3,
            contract_address=self.lido_address,
            contract_abi_path=self.lido_abi_path,
            funcs_to_fetch=funcs_to_fetch,
        )

    def lido_self_check(self):
        """
        Testing interaction with Lido contracts
        """
        nos_contract = get_contract(
            self.w3, address=self.registry_address, path=self.registry_abi_path
        )
        nos_contract.functions.getNodeOperatorsCount().call()
        nos_contract.functions.getNodeOperator(0, True).call()
        nos_contract.functions.getSigningKey(0, 0).call()

        lido_contract = get_contract(self.w3, address=self.lido_address, path=self.lido_abi_path)
        lido_contract.functions.getWithdrawalCredentials().call()
        lido_contract.functions.isStopped().call()
        lido_contract.functions.getTotalPooledEther().call()
        lido_contract.functions.getWithdrawalCredentials().call()
        lido_contract.functions.getFee().call()
        lido_contract.functions.getFeeDistribution().call()
        lido_contract.functions.getBeaconStat().call()
        lido_contract.functions.getBufferedEther().call()

import pytest

from lido.main import Lido
from lido.contracts.abi_loader import load_lido_abi, load_operators_abi
from lido.multicall.constants import MULTICALL_ADDRESSES

from web3.middleware import geth_poa_middleware

from tests.fake_web3 import FakeWeb3, FakeContract
from tests.utils import load_test_data_from_file

import copy


def test_get_operators():
    operators = load_test_data_from_file("operators_data.txt")

    def fake_getNodeOperatorsCount(eth, data):
        return [len(operators)]

    def fake_getNodeOperator(eth, data):
        op_id = data[0]
        op = list(filter(lambda x: x['id'] == op_id, operators))[0]
        return [
                op['active'], 
                op['name'],
                op['rewardAddress'],
                op['stakingLimit'],
                op['stoppedValidators'],
                op['totalSigningKeys'],
                op['usedSigningKeys']
            ]

    def fake_aggregate(eth, data):
        return [0, [
            eth.call({
                'to': MULTICALL_ADDRESSES[web3.eth.chainId],
                'data': x[1]
            }) for x in data[0]
        ]]

    web3 = FakeWeb3()
    web3.eth.chainId = 5
    web3.middleware_onion = [geth_poa_middleware]

    lido = Lido(web3)

    lido_contract = FakeContract(
        lido.registry_address,
        load_lido_abi(lido.registry_abi_path),
        web3.eth)
    lido_contract.add_contract_method(
        "getNodeOperatorsCount()(uint256)",
        fake_getNodeOperatorsCount)
    lido_contract.add_contract_method(
        "getNodeOperator(uint256,bool)(bool,string,address,uint64,uint64,uint64,uint64)",
        fake_getNodeOperator)
    web3.eth.add_contract(lido_contract)

    mcall_contract = FakeContract(
        MULTICALL_ADDRESSES[web3.eth.chainId],
        None,
        web3.eth)
    mcall_contract.add_contract_method(
        "aggregate((address,bytes)[])(uint256,bytes[])",
        fake_aggregate)
    web3.eth.add_contract(mcall_contract)

    operators_data = lido.get_operators_data()

    assert operators_data == operators


def test_get_operators_keys():
    operators = load_test_data_from_file("operators_with_valid_keys_goerly.txt")

    def fake_getSigningKey(eth, data):
        op_id = data[0]
        key_index = data[1]
        op = list(filter(lambda x: x['id'] == op_id, operators))[0]
        key = list(filter(lambda x: x['index'] == key_index, op['keys']))[0]
        return [
                key['key'],
                key['depositSignature'],
                key['used']
            ]

    web3 = FakeWeb3()
    web3.eth.chainId = 5
    web3.middleware_onion = [geth_poa_middleware]

    lido = Lido(web3)
    lido_contract = FakeContract(
        lido.registry_address,
        load_lido_abi(lido.registry_abi_path),
        web3.eth)
    lido_contract.add_contract_method(
        "getSigningKey(uint256,uint256)(bytes,bytes,bool)",
        fake_getSigningKey)
    web3.eth.add_contract(lido_contract)

    operators_with_keys = lido.get_operators_keys(
        [{
            'id': op['id'],
            'totalSigningKeys': op['totalSigningKeys'],
        } for op in operators])

    assert operators == operators_with_keys


def test_validate_valid_keys_goerly():
    operators = load_test_data_from_file("operators_with_valid_keys_goerly.txt")

    web3 = FakeWeb3()
    web3.eth.chainId = 5
    web3.middleware_onion = [geth_poa_middleware]

    lido = Lido(web3)
    lido_contract = FakeContract(
        lido.lido_address,
        load_lido_abi(lido.lido_abi_path),
        web3.eth)
    lido_contract.add_contract_method(
        "getWithdrawalCredentials()(bytes32)",
        lambda eth: b'\x00\x04\x05\x17\xce\x98\xf8\x10p\xce\xa2\x0e5a\n:\xe2:E\xf0\x88;\x0b\x03Z\xfcW\x17\xcc.\x83>')
    web3.eth.add_contract(lido_contract)

    operators_with_validated_keys = lido.validate_keys_multi(operators)

    for op in operators_with_validated_keys:
        for key in op['keys']:
            assert key["valid_signature"]


def test_validate_valid_keys_mainnet():
    operators = load_test_data_from_file("operators_with_valid_keys_mainnet.txt")

    web3 = FakeWeb3()
    web3.eth.chainId = 1
    web3.middleware_onion = []

    lido = Lido(web3)
    lido_contract = FakeContract(
        lido.lido_address,
        load_lido_abi(lido.lido_abi_path),
        web3.eth)
    lido_contract.add_contract_method(
        "getWithdrawalCredentials()(bytes32)",
        lambda eth: b'\x00\x96\x90\xe5\xd4G,|\r\xbd\xf4\x90B]\x89\x86%5\xd2\xa5/\xb6\x863?:\n\x9f\xf5\xd2\x12^')
    web3.eth.add_contract(lido_contract)

    operators_with_validated_keys = lido.validate_keys_multi(operators)

    for op in operators_with_validated_keys:
        for key in op['keys']:
            assert key["valid_signature"]


def test_validate_invalid_keys():
    operators = load_test_data_from_file("operator_with_invalid_key.txt")

    web3 = FakeWeb3()
    web3.eth.chainId = 5
    web3.middleware_onion = [geth_poa_middleware]

    lido = Lido(web3)
    lido_contract = FakeContract(
        lido.lido_address,
        load_lido_abi(lido.lido_abi_path),
        web3.eth)
    lido_contract.add_contract_method(
        "getWithdrawalCredentials()(bytes32)",
        lambda eth: b'\x00\x04\x05\x17\xce\x98\xf8\x10p\xce\xa2\x0e5a\n:\xe2:E\xf0\x88;\x0b\x03Z\xfcW\x17\xcc.\x83>')
    web3.eth.add_contract(lido_contract)

    operators_with_validated_keys = lido.validate_keys_multi(operators)

    for op in operators_with_validated_keys:
        for key in op['keys']:
            assert key["valid_signature"] == False

def test_different_validate_keys_methods():
    operators = load_test_data_from_file("operators_with_mixed_keys_goerly.txt")

    web3 = FakeWeb3()
    web3.eth.chainId = 5
    web3.middleware_onion = [geth_poa_middleware]

    lido = Lido(web3)
    lido_contract = FakeContract(
        lido.lido_address,
        load_lido_abi(lido.lido_abi_path),
        web3.eth)
    lido_contract.add_contract_method(
        "getWithdrawalCredentials()(bytes32)",
        lambda eth: b'\x00\x04\x05\x17\xce\x98\xf8\x10p\xce\xa2\x0e5a\n:\xe2:E\xf0\x88;\x0b\x03Z\xfcW\x17\xcc.\x83>')
    web3.eth.add_contract(lido_contract)

    operators_with_validated_keys_mono = lido.validate_keys_mono(
        copy.deepcopy(operators))
    operators_with_validated_keys_multi = lido.validate_keys_multi(
        copy.deepcopy(operators))

    assert operators_with_validated_keys_mono == \
        operators_with_validated_keys_multi


def test_find_duplicates():
    operators = load_test_data_from_file("operators_with_duplicated_keys_goerly.txt")

    operators_with_checked_duplicates = Lido.find_duplicates(operators)

    assert operators_with_checked_duplicates[0]['keys'][0]['duplicate'] == False
    assert operators_with_checked_duplicates[0]['keys'][1]['duplicate'] == True
    assert operators_with_checked_duplicates[0]['keys'][2]['duplicate'] == True
    assert operators_with_checked_duplicates[1]['keys'][0]['duplicate'] == True
    assert operators_with_checked_duplicates[1]['keys'][1]['duplicate'] == False
    assert operators_with_checked_duplicates[1]['keys'][2]['duplicate'] == False
    assert operators_with_checked_duplicates[2]['keys'][0]['duplicate'] == False
    assert operators_with_checked_duplicates[2]['keys'][1]['duplicate'] == False
    assert operators_with_checked_duplicates[2]['keys'][2]['duplicate'] == True


def test_poa_middleware_check():
    web3_goerly = FakeWeb3()
    web3_goerly.eth.chainId = 5
    web3_goerly.middleware_onion = []
    try:
        Lido(web3_goerly)
        assert False, "No exception while PoA middleware is not injected"
    except(ValueError):
        pass

    web3_mainnet = FakeWeb3()
    web3_mainnet.eth.chainId = 1
    web3_mainnet.middleware_onion = []
    try:
        lido = Lido(web3_mainnet)
    except(ValueError):
        assert False, "Exception while web3 is connected to mainnet"

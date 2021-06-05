import pytest

from lido.main import Lido
from lido.contracts.abi_loader import load_lido_abi, load_operators_abi
from lido.multicall.constants import MULTICALL_ADDRESSES

from web3.middleware import geth_poa_middleware

from tests.fake_web3 import FakeWeb3, FakeContract

import os
import ast
import copy

script_dir = os.path.dirname(__file__)


def test_get_operators():
    with open(os.path.join(script_dir, "operators_data.txt"),
        "r") as test_data:
        operators = ast.literal_eval(test_data.read())

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
    mcall_contract = FakeContract(
        MULTICALL_ADDRESSES[web3.eth.chainId],
        None,
        web3.eth)
    mcall_contract.add_contract_method(
        "aggregate((address,bytes)[])(uint256,bytes[])",
        fake_aggregate)
    web3.eth.add_contract(lido_contract)
    web3.eth.add_contract(mcall_contract)

    operators_data = lido.get_operators_data()

    assert operators_data == operators


def test_get_operators_keys():

    def fake_getSigningKey(eth, data):
        op_id = data[0]
        key_id = data[1]
        return [
            b'\x81\xb4\xaea\xa8\x989i\x03\x89\x7f\x94\xbe\xa0\xe0b\xc3\xa6\x92^\xe9=0\xf4\xd4\xae\xe9;S;IU\x1a\xc37\xdax\xff*\xb0\xcf\xbb\n\xdb8\x0c\xad\x94',
            b'\x96\xa8\x8f\x8e\x88>\x9f\xf6\xf3\x97Q\xa2\xcb\xfc\xa3\x94\x9fO\xa9j\xe9\x84D\xd0\x05\xb6\xea\x9f\xaa\xc0\xc3KR\xd5\x95\xf9B\x8d\x90\x1d\xdd\x815$\x83}\x86d\x01\xedL\xed=\x84\xe7\xe88\xa2e\x06\xae.\xf3\xbf\x0b\xf1\xb8\xd3\x8b+\xd7\xbd\xb6\xc1<_F\xb8H\xd0-\xdc\x11\x08d\x9e\x96\x07\xcfM/\xce\xcd\xd8\x07\xbb',
            True]

    operators = [{'id': 0, 'active': True, 'name': 'Staking Facilities', 'rewardAddress': '0xdd4bc51496dc93a0c47008e820e0d80745476f22', 'stakingLimit': 2040, 'stoppedValidators': 0, 'totalSigningKeys': 2500, 'usedSigningKeys': 2000}, {'id': 1, 'active': True, 'name': 'Staking Facilities', 'rewardAddress': '0xdd4bc51496dc93a0c47008e820e0d80745476f22', 'stakingLimit': 2040, 'stoppedValidators': 0, 'totalSigningKeys': 2500, 'usedSigningKeys': 2000}, {'id': 2, 'active': True, 'name': 'Staking Facilities', 'rewardAddress': '0xdd4bc51496dc93a0c47008e820e0d80745476f22', 'stakingLimit': 2040, 'stoppedValidators': 0, 'totalSigningKeys': 2500, 'usedSigningKeys': 2000}, {'id': 3, 'active': True, 'name': 'Staking Facilities', 'rewardAddress': '0xdd4bc51496dc93a0c47008e820e0d80745476f22', 'stakingLimit': 2040, 'stoppedValidators': 0, 'totalSigningKeys': 2500, 'usedSigningKeys': 2000}]

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

    operators_w_keys = lido.get_operators_keys(operators)

    assert len(operators_w_keys) == 4


def test_validate_valid_keys_goerly():
    with open(os.path.join(script_dir, "operators_with_valid_keys_goerly.txt"),
        "r") as test_data:
        operators = ast.literal_eval(test_data.read())

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
    with open(os.path.join(script_dir, "operators_with_valid_keys_mainnet.txt"),
        "r") as test_data:
        operators = ast.literal_eval(test_data.read())

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
    with open(os.path.join(script_dir, "operator_with_invalid_key.txt"),
        "r") as test_data:
        operators = ast.literal_eval(test_data.read())

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
    with open(os.path.join(script_dir, "operators_with_mixed_keys_goerly.txt"),
        "r") as test_data:
        operators = ast.literal_eval(test_data.read())

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
    with open(os.path.join(script_dir, 
    "operators_with_duplicated_keys_goerly.txt"),
        "r") as test_data:
        operators = ast.literal_eval(test_data.read())

    web3 = FakeWeb3()
    web3.eth.chainId = 1
    web3.middleware_onion = []

    lido = Lido(web3)

    operators_with_checked_duplicates = lido.find_duplicates(operators)

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

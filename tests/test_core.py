from logging import Handler
from lido.main import Lido
from lido.get_operators_keys import get_operators_keys
import pytest
from lido import get_operators_data
from lido.multicall import signature
from lido.multicall.signature import parse_signature
from eth_abi import encode_single, decode_single
from eth_utils import function_signature_to_4byte_selector
from web3.middleware import geth_poa_middleware

class FakeContract:
    abi = None

class FakeEth:
    handlers = {}
    signatures = {}

    def contract(self, address, abi):
        class Function():
            def call(self):
                return b'\x00\x04\x05\x17\xce\x98\xf8\x10p\xce\xa2\x0e5a\n:\xe2:E\xf0\x88;\x0b\x03Z\xfcW\x17\xcc.\x83>'

        class Functions():
            def getWithdrawalCredentials(self):
                return Function()
        c = FakeContract()
        c.abi = abi
        c.functions = Functions()
        return c

    def add_contract_method(self, signature, handler, address=None):
        parts = parse_signature(signature)
        function_with_inputs = "".join(parts[:2])
        sign = function_signature_to_4byte_selector(function_with_inputs)
        self.handlers[sign] = handler
        self.signatures[sign] = signature

    def call(self, arg):
        data = arg['data']
        function_sign = data[:4]
        signature = self.signatures[function_sign]
        psign = parse_signature(signature)
        input_types = psign[1]
        output_types = psign[2]
        input = decode_single(input_types, data[4:])
        handler = self.handlers[function_sign]
        ret = handler(self, input)
        return encode_single(output_types, ret)

class FakeWeb3:
    middleware_onion = [geth_poa_middleware]
    eth = FakeEth()

def test_get_operators():
    def getNodeOperatorsCount(eth, data):
        assert len(data) == 0
        return [4]

    def getNodeOperator(eth, data):
        id = data[0]
        assert data[1] == True
        return [
            True,
            'Staking Facilities', 
            '0xdd4bc51496dc93a0c47008e820e0d80745476f22', 
            2040, 0, 2500, 2000]

    def aggregate(eth, data):
        return [0, [
            eth.call({'data': x[1]}) for x in data[0]
            ]]

    web3 = FakeWeb3()
    web3.eth.chainId = 1
    web3.eth.add_contract_method("getNodeOperatorsCount()(uint256)", getNodeOperatorsCount)
    web3.eth.add_contract_method("getNodeOperator(uint256,bool)(bool,string,address,uint64,uint64,uint64,uint64)", getNodeOperator)
    web3.eth.add_contract_method("aggregate((address,bytes)[])(uint256,bytes[])", aggregate)

    lido = Lido(web3)
    operators = lido.get_operators_data()

    assert len(operators) == 4


def test_get_operators_keys():

    def getSigningKey(eth, data):
        op_id = data[0]
        key_id = data[1]
        return [
            b'\x81\xb4\xaea\xa8\x989i\x03\x89\x7f\x94\xbe\xa0\xe0b\xc3\xa6\x92^\xe9=0\xf4\xd4\xae\xe9;S;IU\x1a\xc37\xdax\xff*\xb0\xcf\xbb\n\xdb8\x0c\xad\x94', 
            b'\x96\xa8\x8f\x8e\x88>\x9f\xf6\xf3\x97Q\xa2\xcb\xfc\xa3\x94\x9fO\xa9j\xe9\x84D\xd0\x05\xb6\xea\x9f\xaa\xc0\xc3KR\xd5\x95\xf9B\x8d\x90\x1d\xdd\x815$\x83}\x86d\x01\xedL\xed=\x84\xe7\xe88\xa2e\x06\xae.\xf3\xbf\x0b\xf1\xb8\xd3\x8b+\xd7\xbd\xb6\xc1<_F\xb8H\xd0-\xdc\x11\x08d\x9e\x96\x07\xcfM/\xce\xcd\xd8\x07\xbb', 
            True]

    operators = [{'id': 0, 'active': True, 'name': 'Staking Facilities', 'rewardAddress': '0xdd4bc51496dc93a0c47008e820e0d80745476f22', 'stakingLimit': 2040, 'stoppedValidators': 0, 'totalSigningKeys': 2500, 'usedSigningKeys': 2000}, {'id': 1, 'active': True, 'name': 'Staking Facilities', 'rewardAddress': '0xdd4bc51496dc93a0c47008e820e0d80745476f22', 'stakingLimit': 2040, 'stoppedValidators': 0, 'totalSigningKeys': 2500, 'usedSigningKeys': 2000}, {'id': 2, 'active': True, 'name': 'Staking Facilities', 'rewardAddress': '0xdd4bc51496dc93a0c47008e820e0d80745476f22', 'stakingLimit': 2040, 'stoppedValidators': 0, 'totalSigningKeys': 2500, 'usedSigningKeys': 2000}, {'id': 3, 'active': True, 'name': 'Staking Facilities', 'rewardAddress': '0xdd4bc51496dc93a0c47008e820e0d80745476f22', 'stakingLimit': 2040, 'stoppedValidators': 0, 'totalSigningKeys': 2500, 'usedSigningKeys': 2000}]

    web3 = FakeWeb3()
    web3.eth.chainId = 1
    web3.eth.add_contract_method("getSigningKey(uint256,uint256)(bytes,bytes,bool)", getSigningKey)

    lido = Lido(web3)
    operators_w_keys = lido.get_operators_keys(operators)

    assert len(operators_w_keys) == 4


def test_validate_keys():

    operators = [{'id': 0, 'active': True, 'name': 'Alex T', 'rewardAddress': '0x1c292814671b60a56c4051caf6e6c5fd583f2ce5', 'stakingLimit': 3, 'stoppedValidators': 0, 'totalSigningKeys': 3, 'usedSigningKeys': 3, 'keys': [{'index': 0, 'key': b'\xa8V\x1b\xec\x1b\x1cY\xdc\x9c\x16\xc0-\xf0\xefY\xe7\xd4u\xadG\xca\xeay\xc4U\xf2\x18\x0f\xae\x96g\xc3\x121\xb9Z\xaf\xc0G7\x99IF\x88\x14\xbf\xa0\xc5', 'depositSignature': b"\x8bM\xde(s\x10Z\xcf\xf7\x13X\x14\xbbO\xd4\xe5r\xbb\xc6\x98\x1d\xfe\xd17kY\xdf\xcb\x16\x82\x8b\x89\x1av\xe2\xf4\x9f\x08\xc7\xb9\xa8\x19\x8f\xa9O\xb3'K\x18\xd0\x9a\xdb\xa6\xb6 \tA\xb5\x1c\x92\xa9\t\xc6\xc2f\xc9\x02'\x07|\xaey\x00YD\xf3\xec\xf25[\xd0!\xb4\xf5\xd7E\xc3\xef]\x84\x13\x15\x8f\xb5;\xb5", 'used': True}, {'index': 1, 'key': b'\xb5\x80\xbc`\xea\x1c\xd9\x0b\x06\x8b\x01\xa9Z\xe2\x9ek\xe9\x8f\x7f!\x1c\x96\xe6\xe7\xbd@U(Y{<\xe5\r\xbb\xd2\xe6\x1c\xf4cD\x93Ye\xd8\xecV\xd7\xd2', 'depositSignature': b'\x82z1s\xc7d\xe8z9kC\x878\xd3\xbe4\x0b~3\xc1~\xf2\xc1\x10\xc4$\x93\x1d\x1aQZ\x8f\xb9\xda\xc1\x91tb\xba9\x05,\xda\xf6\xbd\xc6\x9d\x87\x0eh\xc9E\x82\xe5\xe9BH\xd3\xca\x99\xe5bP?\xb2\xc7~6gO^\xd3\xfa\x87\xd80f\xc2\xed\xff\x1d7\x08z\xf9\xcf\xd2\xc4\xf6\xc3\x04k\x8d\x8b\x92\x12', 'used': True}, {'index': 2, 'key': b'\x8a\xc2\xb0\x03b\xb6\nAj\x0b\xcd\xe4\xa4V\xa9x\xc6{4\x08r\xb2\xda\xba[\xf2\xfbDK?\xd9Y\xec\x9fw\t\x84\xd9\x80\x95 \xf0;\xeb\x8f\x10\xfe\x05', 'depositSignature': b'\xb4M\xfe\xc3Q\xd0\xa0!\xc11\xa1\x92\xeeI\x1f\x82\x95\xe4\xec\xa5\xe88\xe2zic\x9diV\xf4c\xe8L\x87\x13\xd2\x16^\xbc\xa7\xba\x15\xd5\xb7:*P\x8b\x15-H\xc3\x94\x85S\x92\xe4\x8f\xc9\x08\xaeS\xd2\xf43\x18n\x0b\xb9T\xfb\xca\xf9\xa8\x84_\x12\x020\x96\xc7\xc7Q\xcdN\xec\x17\xe7CZ\xcc%\x00%\r ', 'used': True}]}, {'id': 1, 'active': True, 'name': 'KRogLA', 'rewardAddress': '0xa988c92aeaa098c0cf00312efc461f5b0b2f9fc9', 'stakingLimit': 3, 'stoppedValidators': 0, 'totalSigningKeys': 3, 'usedSigningKeys': 3, 'keys': [{'index': 0, 'key': b'\x81ty\x94{`T\xdd[\x1bn\xfc\x19\xdf\x11\xf7\x8f\x94D\xa9\xf8a\xf6\xcbS\x86AR\x85Xk\x84\x18\x02\xe1W\x85-j\xd6o\x96\x18o6\xe4\x0bz', 'depositSignature': b'\x97+-\xb7\xda\xbf\x7f\xca\xa1\x02+\x9ch \xe0N\xd0`\xfc7T\x94\xc4\xa7\x06\xa5\xa7\xdb\x9d\r\xda\n\xcbk1+\xe5\xf6\xe2<x$X\xc7?\x97\xd7\xe7\x02=\x85u\x11\x82\xbe\xa2\x03\x8d\xed^\xfd]:v\xf8\xc8\xb3<\xf8\x91\x1e4\xdau\xd9\xe4\x138\x15\xae8}hh+\xa0\x9c\xa3\xe2\xb2Z\xef\x88\x93\x16\xea', 'used': True}, {'index': 1, 'key': b'\xa3\x81\xf6\x00=*\xe736\xad\xd7\x8e\x02\x13T\xbc\xd5\xe0\x86\xe8\xe5\xfc\x14HrQ\x930M\xde?\xad\xa0\xe8?\xdf\x91\xf7\xddN\x87\x85D\x8a\xa4\xff<\x19', 'depositSignature': b'\xa8\x17\xf1(1\xcc:1\x05\xb2I\x1e\xca\xafz`\xf0T8\x98@\xc6W)\xad+\xde\x95\xd4|v\x8a\xb1G\xd6\x01-3`F\x89$\x17\xe7\xd2\xf6])\x00{\x14)\xd1c\xf6\xa4;\xc8\x9d\xbb^\xda\xa8\xc5\xf0\xe5QJW\x0f\xf9\\\x9e\xe5\x1bR\xf5\xd3\xe0\x05p\x86u\t+lX\xd1\xac\xc9\x82\xc1E3\\\xe1', 'used': True}, {'index': 2, 'key': b'\xac\xb8\x82?\xfaI\xee\x93\xd3r\x91\xec\x1a;\xb0\xd9\x91_#\xb2\x13D\xe4\x1e\x90\xed\xd9\xa8\x98\x85{(\xc2\x9f\xa8\xa3M\xf4\xcf\xde\x19\xbf5\xc7\xf29J\t', 'depositSignature': b'\x8f\xc9\x04RkFt\xdf\x06%+bC8Ki\xc7\\\xa4\xee\x90\xffwF\xf5\xf3\xb3\x8c\xfc\xa9\xbf9\xed;\xe7O\r\xfc$\x1d\xdb\xa6)\x87\xe0\xa6\x15\xa9\x03l\xf0\xab\x91\x08\x8a;\t~D\x15\xe04\xcc\xc5\xdcP\x90\x84\x9fg.\x9c\xd3\xf4D\xbb+\xc8F=\xd9\xdb\xc5\xa4u\xc6\xca\xff0z\xc4\xbfX\xedU|', 'used': True}]}, {'id': 2, 'active': True, 'name': 'Nikolay', 'rewardAddress': '0xec2d2e81721a477798e938924266f92c4e5fc54e', 'stakingLimit': 3, 'stoppedValidators': 0, 'totalSigningKeys': 3, 'usedSigningKeys': 3, 'keys': [{'index': 0, 'key': b'\xa6\x17\xe1\xca\xdeF`\x82\x03\xf9rn:\x05\x08\xad\xc0\xc9\x97- \xb5%\xc8|\xb5!\xb4\x7f\xb82\xa6\x96}\xca|\xb2k\xf6h\x82l\xe8\xc4\x04\x8c\xd5\x01', 'depositSignature': b"\x94\xd4\xb7\xa4\xf7\x07\xae{\x8eYX4e\xd2N\xa9E4E\x06\xec\x8c\xa6\xf4~\x16\x10+\x04\xd9d=i$\x9c\xed\x04\xab\xc5\x8c\xa1\x1f>pi\xb9\xc5\xa9\x13)\x7f\xc6\x01\x8c\xd8\xba\x93\x1e\xb1+\xff\x95\xb93=z\xe4\xaf\\\x1eS\xbf{$\x08'4J\xc4:\x9c]\xdb\x8e\xe9-\x04\n\x96\xf9\x00B\x02\xcc\x8f`", 'used': True}, {'index': 1, 'key': b'\x8b\x12\xccV\xe0\xd4\xe4\x02.\x8a\x9d\xc5TF\xd9\xe0Pm2o\x90+7\x8f\x95saNjx\x90\xd7\x1dE\x04o\xb0h\xa3\x9f\xd9u\xd5e+`\x95\n', 'depositSignature': b'\xb2\xb5\xc4r\xdd\xe0\xae\x90q\xf6\xf89\x92&}\xcbUT\xe7\xb9\xb7\x10 \x1efC\t\xd6#\xe1\x0b)\x94Alw\xca\x94\x184i \xc0\x99\xd9M\x0b^\x182\x9c\xcepJ|\x071\n\xf7\xa1C\xf7\x80C#j\xbb\xac\xb4\x12B\x9f\x0e\x8d\xcc{\xbe}_91\xe7\x14E\x03\x88K\xaeP%sD}\x7f}\\', 'used': True}, {'index': 2, 'key': b'\x8e\xd5\x99\xd0\xd5\x82\x89\x96X^\x99\xf46\xbc\xe2q\x8bE\xa5\xc0Y\xbe\xed\x97Xj\x8f\x0f\\\no\x04B\xee\xee\x96\xd6\x83\xcdm\xed$$\x14F\x99\x18\x89', 'depositSignature': b'\x80mI\xcd\x8c/i#\xea\xfc\xaa\xad\xaf"gQ1d\xaf\t\xb6\x87\xd1\x1c\r@f\xf3\xb4,%\x97u3\t\x00!\x984\xbe\x1fV\xe46\x95\xc8\x08O\x06\xb8v[0\xb7\x81Mo\x11~\x9fk`Z\x18@\xe5\xdc\xfe\x9c\x02\xf0{\xe1\xf7\x97\x0eps\xc7P\x9f\x83w@\xe03n\xd3\x07\xc4\x1c!:\xcb]\x8f', 'used': True}]}]

    web3 = FakeWeb3()
    web3.eth.chainId = 5

    lido = Lido(web3)
    operators_w_v_keys = lido.validate_keys_mono(operators)

    for op in operators_w_v_keys:
        for key in op['keys']:
            assert key["valid_signature"]

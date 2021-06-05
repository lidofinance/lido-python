from lido.multicall.signature import parse_signature
from eth_abi import encode_single, decode_single
from eth_utils import function_signature_to_4byte_selector
from web3.middleware import geth_poa_middleware


class FakeFunction():
    def __init__(self, handler, eth):
        self.handler = handler
        self.eth = eth

    def call(self):
        return self.handler(self.eth)


class FakeContract:
    handlers = {}
    signatures = {}

    def __init__(self, address, abi, eth):
        self.address = address
        self.abi = abi
        self.function_class = type(self.address, (), {})
        self.functions = self.function_class()
        self.eth = eth

    def add_contract_method(self, signature, handler, address=None):
        parts = parse_signature(signature)
        function_with_inputs = "".join(parts[:2])
        sign = function_signature_to_4byte_selector(function_with_inputs)
        self.handlers[sign] = handler
        self.signatures[sign] = signature
        function_object = FakeFunction(handler, self.eth)
        setattr(self.function_class, parts[0], lambda self: function_object)

    def call(self, data):
        function_sign = data[:4]
        signature = self.signatures[function_sign]
        psign = parse_signature(signature)
        input_types = psign[1]
        output_types = psign[2]
        input = decode_single(input_types, data[4:])
        handler = self.handlers[function_sign]
        ret = handler(self.eth, input)
        return encode_single(output_types, ret)


class FakeEth:
    contracts = {}
    handlers = {}
    signatures = {}

    def contract(self, address, abi):
        return self.contracts[address]

    def add_contract(self, contract):
        self.contracts[contract.address] = contract

    def call(self, arg):
        address = arg['to']
        contract = self.contracts[address]
        return contract.call(arg['data'])


class FakeWeb3:
    middleware_onion = [geth_poa_middleware]
    eth = FakeEth()

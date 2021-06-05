from lido.multicall.signature import parse_signature
from eth_abi import encode_single, decode_single
from eth_utils import function_signature_to_4byte_selector


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

    def add_contract_method(self, full_signature_str, handler):
        parts = parse_signature(full_signature_str)
        function_name_with_inputs = "".join(parts[:2])
        signature_bytes = function_signature_to_4byte_selector(
            function_name_with_inputs)
        self.handlers[signature_bytes] = handler
        self.signatures[signature_bytes] = full_signature_str
        function_object = FakeFunction(handler, self.eth)
        setattr(self.function_class, parts[0], lambda self: function_object)

    def call(self, data):
        signature_bytes = data[:4]
        full_signature_str = self.signatures[signature_bytes]
        parsed_signature = parse_signature(full_signature_str)
        input_types = parsed_signature[1]
        output_types = parsed_signature[2]
        input_data = decode_single(input_types, data[4:])
        handler = self.handlers[signature_bytes]
        result = handler(self.eth, input_data)
        return encode_single(output_types, result)


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
    eth = FakeEth()

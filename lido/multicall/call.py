from eth_utils import to_checksum_address
from lido.multicall import Signature


class Call:
    def __init__(self, w3, target, function, returns=None):
        self.target = to_checksum_address(target)
        if isinstance(function, list):
            self.function, *self.args = function
        else:
            self.function = function
            self.args = None
        self.w3 = w3
        self.signature = Signature(self.function)
        self.returns = returns

    @property
    def data(self):
        return self.signature.encode_data(self.args)

    def decode_output(self, output):
        decoded = self.signature.decode_data(output)

        if self.returns:
            return {
                name: handler(value) if handler else value
                for (name, handler), value in zip(self.returns, [decoded])
            }
        else:
            return decoded if len(decoded) > 1 else decoded[0]

    def __call__(self, args=None):
        args = args or self.args
        calldata = self.signature.encode_data(args)
        output = self.w3.eth.call({"to": self.target, "data": calldata})
        return self.decode_output(output)

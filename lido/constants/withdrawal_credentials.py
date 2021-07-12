# Existing withdrawal credentials on the chain
# Will be filtered for unique values
# Will be used as a fallback for used keys or in strict mode when validating signatures
WITHDRAWAL_CREDENTIALS = {
    "mainnet": ["0x009690e5d4472c7c0dbdf490425d89862535d2a52fb686333f3a0a9ff5d2125e"],
    "goerli": ["0x00040517ce98f81070cea20e35610a3ae23a45f0883b0b035afc5717cc2e833e"],
}


def get_withdrawal_credentials(network):
    wcs = WITHDRAWAL_CREDENTIALS[network]

    formatted = []

    for wc in wcs:
        # Cutting 0x from withdrawal credentials
        # Converting to bytes
        formatted.append(bytes.fromhex(wc[2:]))

    return formatted

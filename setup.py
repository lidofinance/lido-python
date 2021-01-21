"""Setup script for Lido"""

import os.path
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setup(
    name="Lido",
    version="0.1.0",
    description="Network helpers for Lido",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lidofinance/lido-network-helpers",
    author="Lido",
    author_email="info@lido.fi",
    license="MIT",
    packages=["lido"],
    include_package_data=True,
    install_requires=["web3", "py_ecc", "ssz"],
    python_requires=">=3.0,<4",
)

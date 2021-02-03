"""Setup script for Lido"""

import os.path
from setuptools import setup, find_namespace_packages

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setup(
    name="Lido",
    version="0.1.1",
    description="Network helpers for Lido",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lidofinance/lido-python",
    author="Lido",
    author_email="info@lido.fi",
    license="MIT",
    packages=find_namespace_packages(),
    include_package_data=True,
    install_requires=["web3", "py_ecc", "ssz", "requests"],
    python_requires=">=3.0,<4",
)

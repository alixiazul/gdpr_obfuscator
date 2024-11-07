""" This file allows the module to be installed via pip """

from setuptools import setup, find_packages

setup(
    name="gdpr_obfuscator",
    version="1.0",
    packages=find_packages(),
    install_requires=[],
    test_requires=["pytest"],
    setup_requires=["pytest-runner"], # Allow pytest to be run directly via python setup.py test
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
)
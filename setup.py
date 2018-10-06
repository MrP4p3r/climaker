"""CliMaker argument parser library setup.py"""

from setuptools import setup, find_packages


setup(
    name='climaker',
    version='0.1.0',
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.6.0',
    test_suite='tests',
)

"""CliMaker argument parser library setup.py"""

from setuptools import setup, find_packages


with open('README.md') as readme_file:
    long_description = readme_file.read()

setup(
    name='climaker',
    version='0.1.0',
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.6.0',
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: User Interfaces',
    ],
    url='https://github.com/MrP4p3r/climaker',
    description='Build a CLI parser with subcommands',
    long_description=long_description,
    long_description_content_type='text/markdown',
)

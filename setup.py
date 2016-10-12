#!/usr/bin/env python

from setuptools import find_packages, setup

requirements = map(lambda x: x.strip(), open('requirements.txt').readlines())

config = {
    'description': 'A high performance compressed columnar data store for Pandas DataFrames',
    'author': 'Josh Levy-Kramer',
    'url': 'https://github.com/joshlk/blosc_store',
    'version': '0.1',
    'packages': find_packages(exclude=('tests', 'tests.*')),
    'include_package_data': True,
    'name': 'blosc_store',
    'install_requires': requirements,
    'license': 'MIT License'
}

setup(**config)

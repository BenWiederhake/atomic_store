#!/usr/bin/env python3
# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.

import sys
import pkgutil
from setuptools import setup
from setuptools.command.install import install


setup(
    name='atomic_store',
    version='0.0.1',
    packages=['atomic_store'],
    install_requires=['atomicwrites>=1.3.0'],  # A lower version might be fine
    author='Ben Wiederhake',
    author_email='BenWiederhake.GitHub@gmx.de',
    description='A robust, atomic file store',
    long_description='A store that is easier than a DBMS, but more fault-resistant than just naive files.',
    platforms='Any',
    license='MIT',
    keywords='atomic store',
    url='https://github.com/BenWiederhake/atomic_store',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    cmdclass={'install': install}
)

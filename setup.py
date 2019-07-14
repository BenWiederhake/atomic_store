#!/usr/bin/env python3
# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.

from setuptools import setup


setup(
    name='atomic_store',
    version='0.0.1',
    packages=['atomic_store'],
    install_requires=['atomicwrites>=1.3.0', 'bson>=0.5.8'],  # Lower versions might be fine
    author='Ben Wiederhake',
    author_email='BenWiederhake.GitHub@gmx.de',
    description='A robust, atomic single-file value store',
    long_description='Easier than a DBMS, but more fault-resistant than just a file.',
    platforms='Any',
    license='MIT',
    keywords='atomic store',
    url='https://github.com/BenWiederhake/atomic_store',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)

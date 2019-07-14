#!/usr/bin/env python3
# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.

import os.path
import shutil
import tempfile
import unittest

import atomic_store


class TestStore(unittest.TestCase):
    def __init__(self, *args):
        super().__init__(*args)
        self._is_set_up = False

    def setUpStore(self, **store_kwargs):
        assert not self._is_set_up
        self._is_set_up = True
        self.store_kwargs = store_kwargs
        # We want to `mk*temp` to actually create *something* in order to raise
        # the chances of it being actually atomic.  However, we don't want it
        # to create a *file*, because `atomic_store` treats empty files and
        # non-existent files differently.  So we atomically create a folder,
        # and hope that we're the only test with that particular folder.
        self.temp_prefix = tempfile.mkdtemp(prefix='test_atomic_store_')
        self.store_path = tempfile.mktemp(prefix='test_atomic_store_', dir=self.temp_prefix)

    def tearDown(self):
        shutil.rmtree(self.temp_prefix)

    def open_store(self):
        return atomic_store.open(self.store_path, **self.store_kwargs)

    def assertFile(self, expected_content):
        if expected_content is None:
            self.assertFalse(os.path.exists(self.store_path))
            return
        if isinstance(expected_content, str):
            mode = 'r'
        elif isinstance(expected_content, bytes):
            mode = 'rb'
        else:
            self.fail('expected_content must be either bytes or str!')
            return
        self.assertTrue(os.path.exists(self.store_path))
        with open(self.store_path, mode) as fp:
            actual_content = fp.read()
        self.assertEqual(expected_content, actual_content)

#!/usr/bin/env python3
# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.

import atomic_store
import os.path
import shutil
import tempfile
import time
import unittest

# Run all the snippets in the README.
class TestReadme(unittest.TestCase):
    def setUp(self):
        self.temp_prefix = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_prefix)

    def path_to(self, name):
        return os.path.join(self.temp_prefix, name)

    def test_usage_ctx_mngr(self):
        path = self.path_to('runs.json')
        self.assertFalse(os.path.exists(path))
        with atomic_store.open(path, default=[]) as store:
            self.assertFalse(os.path.exists(path))
            self.assertEqual([], store.value)
            new_entry = '1234'
            store.value.append(new_entry)
            self.assertFalse(os.path.exists(path))
            self.assertEqual(['1234'], store.value)
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as fp:
            self.assertEqual(fp.read(), '["1234"]')
        self.assertEqual(['1234'], store.value)
        with atomic_store.open(path, default=[]) as store:
            self.assertTrue(os.path.exists(path))
            with open(path, 'r') as fp:
                self.assertEqual(fp.read(), '["1234"]')
            self.assertEqual(['1234'], store.value)
            new_entry = '5678'
            store.value.append(new_entry)
            self.assertTrue(os.path.exists(path))
            with open(path, 'r') as fp:
                self.assertEqual(fp.read(), '["1234"]')
            self.assertEqual(['1234', '5678'], store.value)
        with open(path, 'r') as fp:
            self.assertEqual(fp.read(), '["1234", "5678"]')
        self.assertEqual(['1234', '5678'], store.value)

#!/usr/bin/env python3
# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.

from . import metastore


# Run all the snippets in the README.
class TestReadme(metastore.TestStore):
    def setUp(self):
        self.setUpStore(default=[])

    def test_usage_ctx_mngr(self):
        self.assertFile(None)
        with self.open_store() as store:
            self.assertFile(None)
            self.assertEqual([], store.value)
            new_entry = '1234'
            store.value.append(new_entry)
            self.assertFile(None)
            self.assertEqual(['1234'], store.value)
        self.assertFile('["1234"]')
        self.assertEqual(['1234'], store.value)
        with self.open_store() as store:
            self.assertFile('["1234"]')
            self.assertEqual(['1234'], store.value)
            new_entry = '5678'
            store.value.append(new_entry)
            self.assertFile('["1234"]')
            self.assertEqual(['1234', '5678'], store.value)
        self.assertFile('["1234", "5678"]')
        self.assertEqual(['1234', '5678'], store.value)

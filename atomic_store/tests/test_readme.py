#!/usr/bin/env python3
# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.

from . import metastore


class TestContextManager(metastore.TestStore):
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


class TestManualControl(metastore.TestStore):
    def setUp(self):
        self.setUpStore(default=dict())

    def test_usage_manual_control(self):
        self.assertFile(None)
        my_store = self.open_store()
        self.assertFile(None)
        self.assertEqual(dict(), my_store.value)
        my_store.value['state'] = 'running'
        my_store.value['thought'] = 'I would not eat green eggs and ham.'
        self.assertFile(None)
        self.assertEqual({"state": "running", "thought": "I would not eat green eggs and ham."}, my_store.value)
        my_store.commit()
        self.assertFile('{"state": "running", "thought": "I would not eat green eggs and ham."}')
        self.assertEqual({"state": "running", "thought": "I would not eat green eggs and ham."}, my_store.value)
        # ... some calculations ...
        my_store.value['state'] = 'done'
        my_store.value['thought'] = 'I do so like Green eggs and ham!'
        self.assertFile('{"state": "running", "thought": "I would not eat green eggs and ham."}')
        self.assertEqual({"state": "done", "thought": "I do so like Green eggs and ham!"}, my_store.value)
        my_store.commit()
        self.assertFile('{"state": "done", "thought": "I do so like Green eggs and ham!"}')
        self.assertEqual({"state": "done", "thought": "I do so like Green eggs and ham!"}, my_store.value)


class TestFormatTweak(metastore.TestStore):
    def test_compact_format(self):
        self.setUpStore(default=dict(), dump_kwargs=dict(sort_keys=True, separators=(',', ':')))
        self.assertFile(None)
        with self.open_store() as store:
            store.value['b'] = 1337
            store.value['a'] = 2
            self.assertEqual({'b': 1337, 'a': 2}, store.value)
        # Note the order!
        self.assertFile('{"a":2,"b":1337}')

    def test_indented_format(self):
        dump_kwargs = dict(indent=1, separators=(' ,', '  : '))
        self.setUpStore(default=dict(), dump_kwargs=dump_kwargs, load_kwargs=dict())
        self.assertFile(None)
        with self.open_store() as store:
            store.value['b'] = 1337
            store.value['a'] = 2
            self.assertEqual({'b': 1337, 'a': 2}, store.value)
        # Note the order!
        self.assertFile('{\n "b"  : 1337 ,\n "a"  : 2\n}')

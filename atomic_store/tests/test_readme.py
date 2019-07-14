#!/usr/bin/env python3
# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.

import atomic_store
import bson
import json
import pickle

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


class CustomFormatBstr(atomic_store.AbstractFormatBstr):
    def __init__(self, t):
        self.t = t

    def dumps(self, obj, **kwargs):
        self.t.assertEqual(obj, ['A6QemadVWenL1LR0ueef'])
        return b'f8oDYtZ8zJMZVXIVjTv6'

    def loads(self, binary_string, **kwargs):
        self.t.assertIsInstance(binary_string, bytes)
        self.t.assertEqual(binary_string, b'f8oDYtZ8zJMZVXIVjTv6')
        return ['A6QemadVWenL1LR0ueef']


class CustomBinaryFormatFile(atomic_store.AbstractFormatFile):
    def __init__(self, t):
        self.t = t

    def dump(self, obj, fp, **kwargs):
        self.t.assertEqual(obj, ['hUFKTouDel2TY5AvsGoz'])
        fp.write(b'0kCEg4gP022IxuFJdTkj')

    def load(self, fp, **kwargs):
        bstr = fp.read()
        self.t.assertIsInstance(bstr, bytes)
        self.t.assertEqual(bstr, b'0kCEg4gP022IxuFJdTkj')
        return ['hUFKTouDel2TY5AvsGoz']


class CustomTextFormatFile:  # Doesn't need to be a subclass!
    def __init__(self, t):
        self.t = t

    def dump(self, obj, fp, **kwargs):
        self.t.assertEqual(obj, ['TImn6grYvfYQX4w8Ng7Q'])
        fp.write('RpOwTCijMQoRN3Y0SoJR')

    def load(self, fp, **kwargs):
        bstr = fp.read()
        self.t.assertIsInstance(bstr, str)
        self.t.assertEqual(bstr, 'RpOwTCijMQoRN3Y0SoJR')
        return ['TImn6grYvfYQX4w8Ng7Q']


class TestFormats(metastore.TestStore):
    def test_json_string(self):
        self.setUpStore(default=[], format='json')
        self.assertFile(None)
        with self.open_store() as store:
            store.value.append('spanish inquisition')
        self.assertFile('["spanish inquisition"]')
        with self.open_store() as store:
            self.assertEqual(store.value, ['spanish inquisition'])

    def test_json_module(self):
        self.setUpStore(default=[], format=json)
        self.assertFile(None)
        with self.open_store() as store:
            store.value.append('spanish inquisition')
        self.assertFile('["spanish inquisition"]')
        with self.open_store() as store:
            self.assertEqual(store.value, ['spanish inquisition'])

    def test_pickle_string(self):
        self.setUpStore(default=[], format='pickle')
        self.assertFile(None)
        with self.open_store() as store:
            store.value.append('spanish inquisition')
        self.assertFile(b'\x80\x03]q\x00X\x13\x00\x00\x00spanish inquisitionq\x01a.')
        with self.open_store() as store:
            self.assertEqual(store.value, ['spanish inquisition'])

    def test_pickle_module(self):
        self.setUpStore(default=[], format=pickle)
        self.assertFile(None)
        with self.open_store() as store:
            store.value.append('spanish inquisition')
        self.assertFile(b'\x80\x03]q\x00X\x13\x00\x00\x00spanish inquisitionq\x01a.')
        with self.open_store() as store:
            self.assertEqual(store.value, ['spanish inquisition'])

    def test_bson_string(self):
        self.setUpStore(default=dict(), format='bson')
        self.assertFile(None)
        with self.open_store() as store:
            store.value['rabbit'] = 'Caerbannog'
        self.assertFile(b'\x1c\x00\x00\x00\x02rabbit\x00\x0b\x00\x00\x00Caerbannog\x00\x00')
        with self.open_store() as store:
            self.assertEqual(store.value, {'rabbit': 'Caerbannog'})

    def test_bson_module(self):
        self.setUpStore(default=dict(), format=bson)
        self.assertFile(None)
        with self.open_store() as store:
            store.value['rabbit'] = 'Caerbannog'
        self.assertFile(b'\x1c\x00\x00\x00\x02rabbit\x00\x0b\x00\x00\x00Caerbannog\x00\x00')
        with self.open_store() as store:
            self.assertEqual(store.value, {'rabbit': 'Caerbannog'})

    def test_custom_bstr(self):
        self.setUpStore(default=[], format=CustomFormatBstr(self))
        self.assertFile(None)
        with self.open_store() as store:
            store.value.append('A6QemadVWenL1LR0ueef')
        self.assertFile(b'f8oDYtZ8zJMZVXIVjTv6')
        with self.open_store() as store:
            self.assertEqual(store.value, ['A6QemadVWenL1LR0ueef'])

    def test_custom_binfile(self):
        self.setUpStore(default=[], format=CustomBinaryFormatFile(self))
        self.assertFile(None)
        with self.open_store() as store:
            store.value.append('hUFKTouDel2TY5AvsGoz')
        self.assertFile(b'0kCEg4gP022IxuFJdTkj')
        with self.open_store() as store:
            self.assertEqual(store.value, ['hUFKTouDel2TY5AvsGoz'])

    def test_custom_textfile(self):
        self.setUpStore(default=[], format=CustomTextFormatFile(self), is_binary=False)
        self.assertFile(None)
        with self.open_store() as store:
            store.value.append('TImn6grYvfYQX4w8Ng7Q')
        self.assertFile('RpOwTCijMQoRN3Y0SoJR')
        with self.open_store() as store:
            self.assertEqual(store.value, ['TImn6grYvfYQX4w8Ng7Q'])

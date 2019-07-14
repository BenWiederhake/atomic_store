import sys
import unittest

from . import metastore


DICT_KEEPS_INSERTION_ORDER = \
    (sys.version_info.major, sys.version_info.minor, sys.version_info.micro) >= (3, 6, 0)


class TestJsonOrder(metastore.TestStore):
    @unittest.skipIf(not DICT_KEEPS_INSERTION_ORDER, 'Can only check order if it is defined')
    def test_order(self):
        self.setUpStore(default=dict())
        self.assertFile(None)
        with self.open_store() as store:
            store.value['b'] = 1337
            store.value['a'] = 2
            store.value['c'] = 42
            store.value['zz'] = -1
            store.value['fancy'] = 3
        self.assertFile('{"b": 1337, "a": 2, "c": 42, "zz": -1, "fancy": 3}')

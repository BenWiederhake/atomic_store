#!/usr/bin/env python3
# Copyright (c) 2019, Ben Wiederhake
# MIT license.    See the LICENSE file included in the package.

import unittest


class TestNull(unittest.TestCase):
    def test_null(self):
        self.assertEqual(1, 1)
        self.assertEqual('x', 'x')

    @unittest.skip
    def test_fail(self):
        self.assertEqual('a', 'b')

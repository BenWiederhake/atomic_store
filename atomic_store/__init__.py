# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.
"""Easier than a DBMS, but more fault-resistant than just a file.

Sometimes you need to manage a bit of state across executions.
Sometimes, a fully-blown database is just too much.

This library makes it easy to keep a *store* of stuff in a JSON file,
in an atomic and fault-resistant manner.

Other formats (like pickle and bson) are also supported,
and arbitrary formats are possible.
"""

from ._impl import AbstractFormatBstr, AbstractFormatFile, AtomicStore

from ._impl import open_store as open

__all__ = ['AbstractFormatBstr', 'AbstractFormatFile', 'AtomicStore', 'open']

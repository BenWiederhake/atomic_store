# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.

import json
import os.path
import pickle

import atomicwrites


def open_writable(path, is_binary):
    mode = 'wb' if is_binary else 'w'
    return atomicwrites.AtomicWriter(path, mode=mode, overwrite=True).open()


def open_readable(path, is_binary):
    mode = 'rb' if is_binary else 'r'
    return open(path, mode)


class AbstractFormatBstr:
    def dumps(self, obj, **kwargs):
        raise NotImplementedError('atomic_store.AbstractFormatBstr.dump_bstr()')

    def loads(self, binary_string, **kwargs):
        raise NotImplementedError('atomic_store.AbstractFormatBstr.load_bstr()')


class AbstractFormatFile:
    def dump(self, obj, fp, **kwargs):
        raise NotImplementedError('atomic_store.AbstractFormatFile.dump_bstr()')

    def load(self, fp, **kwargs):
        raise NotImplementedError('atomic_store.AbstractFormatFile.load_bstr()')


class WrapBinaryFormat:
    def __init__(self, format_bstr):
        self.format_bstr = format_bstr

    def dump(self, obj, fp, **kwargs):
        bstr = self.format_bstr.dumps(obj, **kwargs)
        fp.write(bstr)

    def load(self, fp, **kwargs):
        bstr = fp.read()
        return self.format_bstr.loads(bstr, **kwargs)


class AtomicStore:
    def __init__(self, path, default, format, is_binary,
                 load_kwargs, dump_kwargs, ignore_inner_exits):
        self.path = path
        self.format = format
        self.is_binary = is_binary
        self.load_kwargs = load_kwargs
        self.dump_kwargs = dump_kwargs
        self.ignore_inner_exits = ignore_inner_exits
        self.level = 0

        if not os.path.exists(self.path):
            self.value = default
        else:
            with open_readable(self.path, self.is_binary) as fp:
                self.value = self.format.load(fp, **self.load_kwargs)

    def commit(self):
        with open_writable(self.path, self.is_binary) as fp:
            self.format.dump(self.value, fp, **self.dump_kwargs)

    def __enter__(self):
        self.level += 1
        return self

    def __exit__(self, _1, _2, _3):
        self.level -= 1
        assert self.level >= 0, 'Reached stacking level {}.  What?!'.format(self.level)
        if self.level == 0 or not self.ignore_inner_exits:
            self.commit()


def _get_bson_module(magic=[]):
    if not magic:
        try:
            import bson
        except ModuleNotFoundError:
            raise ValueError('bson format not suppoerted (bson not installed)')
        magic.append(bson)
    return magic[0]


def resolve_format(format):
    if format is None or format == 'json' or format == json:
        return False, json
    if format == 'bson':
        return True, WrapBinaryFormat(_get_bson_module())
    if format == 'pickle':
        return True, pickle
    if getattr(format, 'dump', None) and getattr(format, 'load', None):
        return True, format
    if getattr(format, 'dumps', None) and getattr(format, 'loads', None):
        return True, WrapBinaryFormat(format)
    raise ValueError('Format not recognized', format)


def open_store(path, default=None, format=None, is_binary=None,
               load_kwargs=None, dump_kwargs=None, ignore_inner_exits=False):
    is_binary_hint, format = resolve_format(format)
    if is_binary is None:
        is_binary = is_binary_hint
    if load_kwargs is None:
        load_kwargs = dict()
    if dump_kwargs is None:
        dump_kwargs = dict()
    return AtomicStore(path, default, format, is_binary,
                       load_kwargs, dump_kwargs, ignore_inner_exits)

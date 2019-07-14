# Copyright (c) 2019, Ben Wiederhake
# MIT license.  See the LICENSE file included in the package.
# This documentation uses NumPy style.  I recommend numpydoc.

import json
import os.path
import pickle

import atomicwrites


def _open_writable(path, is_binary):
    mode = 'wb' if is_binary else 'w'
    return atomicwrites.AtomicWriter(path, mode=mode, overwrite=True).open()


def _open_readable(path, is_binary):
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
            with _open_readable(self.path, self.is_binary) as fp:
                self.value = self.format.load(fp, **self.load_kwargs)

    def commit(self):
        with _open_writable(self.path, self.is_binary) as fp:
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
    """Resolves a format indication in a best-effort manner.

    Given any format indication (e.g. `None`, the module `bson`, the string
    `'pickle'`, or an object), returns something usable.  Specifically,
    the returned format is guaranteed to have the `dump` and `load` attributes,
    and a hint whether these seem to operate on binary or text files.

    Parameters
    ----------
    format : None or module or str or AbstractFormatBstr or AbstractFormatFile or object
        A format indication.

    Returns
    -------
    (bool, object)
        The bool indicates whether this format operates on binary files
        (True for everything except JSON).  The object is guaranteed to
        support the `dump` and `load` attribute
    """
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
    r"""Opens a new atomic store.  Main entry point for `atomic_store`.

    This opens a new store at the given `path`.  The returned object allows
    for easy atomic updates using `.commit()`.
    For more details, see `AtomicStore`.

    Parameters
    ----------
    path : str or path
        Path to a file.  This file may or may not already exist.
    default : any
        If the file at `path` did not already exist, this value is used to
        initialize the store.  Defaults to `None`.
    format : None or module or str or AbstractFormatBstr or AbstractFormatFile or object
        A format indication
        Supported values are `None` (for JSON), `'json'`, `'pickle'`,
        `'bson'` (requires bson to be installed), and also any module or object
        providing `dump/load` or `dumps/loads`.
        Note that this means you can use the modules `json`, `pickle`,
        and `bson` as they are.

    Returns
    -------
    AtomicStore
        The constructed store.  You call `commit()` on it to atomically write
        the stored value to disk, or use it as a context manager to
        automatically trigger a write at the end.

    Other Parameters
    ----------------
    is_binary : None or bool
        By default, `atomic_store` assumes you operate on binary files,
        except when JSON is involved (then it assumes text files).
        To override this, you can set `is_binary`.
    dump_kwargs : None or dict
        This will be forwarded to the `dump` call as-is.
        You can use this for example to pass `separators=(',', ':')` to the JSON encoder.
    load_kwargs : None or dict
        This will be forwarded to the `load` call as-is.
        You can use this for example to pass `encoding='latin-1'` to the pickle decoder.
    """
    is_binary_hint, format = resolve_format(format)
    if is_binary is None:
        is_binary = is_binary_hint
    if load_kwargs is None:
        load_kwargs = dict()
    if dump_kwargs is None:
        dump_kwargs = dict()
    return AtomicStore(path, default, format, is_binary,
                       load_kwargs, dump_kwargs, ignore_inner_exits)

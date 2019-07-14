# atomic_store

> Easier than a DBMS, but more fault-resistant than just a file.

Sometimes you need to manage a bit of state across executions.
Sometimes, a fully-blown database is just too much.

This library makes it easy to keep a *store* of stuff in a JSON file,
in an atomic and fault-resistant manner.

Other formats (like pickle and bson) are also supported,
and arbitrary formats are possible.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [TODOs](#todos)
- [NOTDOs](#notdos)
- [Contribute](#contribute)

## Install

Just `pip install atomic_store`.  Or, if you must, `pip install -r requirements.txt`

Note that the only dependency is `atomicwrites`, which has no dependencies.

## Usage

By default, the store is encoded as json, written to a temporary file,
and then atomically replaces the old file.  When reading, if the file does
not exist, a default value is used.  The default default value is `None`.

### Context Manager

This program remembers all start times:

```python3
import atomic_store
import time

with atomic_store.open('runs.json', default=[]) as store:
    print('Previous executions:')
    print(store.value)
    new_entry = time.strftime('%Y-%m-%d %H:%M:%S%z')
    store.value.append(new_entry)
```

Leaving the context manager takes care of all writes.
No intermediate values get written to disk.

This is ideal if the task runs short, and in case of any error
you only want to keep the old state anyway.

For advanced uses, also see the subsection on [reentrancy](#reentrancy).

### Manual control

This program remembers all start times:

```python3
import atomic_store

my_store = atomic_store.open('gathered.json', default=dict())

my_store.value['state'] = 'running'
my_store.value['thought'] = 'I would not eat green eggs and ham.'
my_store.commit()
# ... some calculations ...
my_store.value['state'] = 'done'
my_store.value['thought'] = 'I do so like Green eggs and ham!'
my_store.commit()
```

Only calls to `commit()` cause writes to the disk.
Again, no intermediate values get written to disk.

This is ideal if you have a long-running job with clear steps,
and each step's output is valuable.

Note that `commit()` is also available in the context manager.

### Format tweaks

If you're using the json backend, and want to keep the JSON file as small as possible,
you can call `open` with `dump_kwargs=dict(separators=(',', ':'))`.
The keyword `load_kwargs` also exists.

### Non-JSON formats

You can use arbitrary other formats, using the `format` keyword:

```python
atomic_store.open('runs.json', default=[], format=MY_FORMAT)
```

Supported values are `None` (for JSON), `'json'`, `'pickle'`,
`'bson'` (requires bson to be installed), and also any module or object
providing `dump/load` or `dumps/loads`.
By default, `atomic_store` assumes you operate on binary files, except when JSON is involved.
To override this, you can set `is_binary`.
Note that this means you can use the modules `json`, `pickle`, and `bson` as they are.

For convenience, you can also override the abstract classes
`atomic_store.AbstractFormatFile` or `atomic_store.AbstractFormatBstr`.

In all cases, `load_kwargs` and `dump_kwargs` are still supported.

### Reentrancy

If the same `atomic_store` is used as a context manager more than once,
the default behavior is to write the file only when the last `with` is exited:

```python
# Assume `state.json` contains only `"before"`.
mngr = atomic_store.open('mystate.json', default=[])
with mngr as store:
    store.value = 'outer'
    # File contains `"before"`: We haven't exited any context manager yet.
    with mngr as store:
        store.value = 'inner'
        # File contains `"before"`: We haven't exited any context manager yet.
    # File now contains `"inner"`, because the inner `with`-statement wrote it.
    # Read the Reentrancy section if you consider this undesired behavior.
# File now contains `"inner"`, because the outer `with`-statement wrote it again.
```

If you consider this behavior undesirable, you can either just use multiple context managers (by calling `atomic_store.open` multiple times), or by using the keyword `ignore_inner_exits=True`, like this:

```python
# Assume `state.json` contains only `"before"`.
mngr = atomic_store.open('mystate.json', default=[], ignore_inner_exits=True)
with mngr as store:
    store.value = 'outer'
    # File contains `"before"`: We haven't exited any context manager yet.
    with mngr as store:
        store.value = 'inner'
        # File contains `"before"`: We haven't exited any context manager yet.
    # File *still* contains `"before"`, as the manager detected that it is still active.
# File now contains `"outer"`, because the outer `with`-statement wrote it.
```

### Atomic is not magic

This library is not magical.

If two threads (or two processes, or whatever) open a store,
modify something, and then write concurrently, one of the results may be lost.
However, the writes are guaranteed to be atomic,
so the data is merely lost, but not corrupted.

## TODOs

* Figure out how to make `bson` optional
* Publish on PyPI

## NOTDOs

Here are some things this project will not support:
* Any DB backend.
* Any multi-file backend.
* More advanced semantics than just `commit`.
* This includes rollback.  It's just not obvious which behavior is desired when the file does not exist (Re-use `default` value?  What if it was modified, as it happens with lists and dicts?), and with stacked context managers (should it rollback to the file's state?  Or to the beginning of the `with`?)

## Contribute

Feel free to dive in! [Open an issue](https://github.com/BenWiederhake/atomic_store/issues/new) or submit PRs.

# atomic_store

> Easier than a DBMS, but more fault-resistant than just a file.

Sometimes you need to manage a bit of state across executions.
Sometimes, a fully-blown database is just too much.

This library makes it easy to keep a *store* of stuff in a JSON file,
in an atomic and fault-resistant manner.  Note that `atomic_store` is not reentrant.

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

### Manual control

This program remembers all start times:

```python3
import atomic_store
import time

my_store = atomic_store.open('gathered.json', default={})

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

### Format tweaks

By default, `atomic_store` tries to keep the JSON file as small as possible.
This means it calls `json.dumps` with the parameters `separators=(',', ':')`.
If you wish any other parameters, you can call `open` with `dump_kwargs=YOUR_KWARGS`.
Note that you have to set `separators=(',', ':')` yourself, if you wish the JSON output to be small.
The option `load_kwargs` is also provided.

### Non-JSON formats

You can use arbitrary other formats, using the `format` keyword:

```python
atomic_store.open('runs.json', default=[], format=MY_FORMAT)
```

Supported values are `None` (for JSON), `'json'`, `'pickle'`,
`'bson'` (requires bson to be installed), and also any module or object
providing `dump` and `load` (operating on files) or `dumps` and `loads` (compatible with binary strings).
Note that this includes the modules `json`, `pickle`, and `bson`.

For convenience, you can also override the abstract classes
`atomic_store.AbstractFormatFile` or `atomic_store.AbstractFormatBstr`.

In all cases, `load_kwargs` and `dump_kwargs` are still supported.

### Not reentrant

This library is not reentrant.

If two threads (or two processes, or whatever) open a store,
modify something, and then write concurrently, one of the results may be lost.
However, the writes are guaranteed to be atomic,
so the data is merely lost, but not corrupted.

## TODOs

* Implement it
* Write tests

## NOTDOs

Here are some things this project will not support:
* Any DB backend.
* Any multi-file backend.
* More advanced semantics than just `commit`.

## Contribute

Feel free to dive in! [Open an issue](https://github.com/BenWiederhake/atomic_store/issues/new) or submit PRs.

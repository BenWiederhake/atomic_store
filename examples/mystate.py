#!/usr/bin/env python3

import atomic_store

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

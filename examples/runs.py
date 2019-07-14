#!/usr/bin/env python3

import atomic_store
import time

with atomic_store.open('runs.json', default=[]) as store:
    print('Previous executions:')
    print(store.value)
    new_entry = time.strftime('%Y-%m-%d %H:%M:%S%z')
    store.value.append(new_entry)

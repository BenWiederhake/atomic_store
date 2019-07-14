#!/usr/bin/env python3

import atomic_store

my_store = atomic_store.open('gathered.json', default=dict())

my_store.value['state'] = 'running'
my_store.value['thought'] = 'I would not eat green eggs and ham.'
my_store.commit()
# ... some calculations ...
my_store.value['state'] = 'done'
my_store.value['thought'] = 'I do so like Green eggs and ham!'
my_store.commit()

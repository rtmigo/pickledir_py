A cache for storing objects inside a file directory.

Object keys can be any string. Objects must be pickle serializable.

---

Unit-tested with Python 3.6-3.9 on macOS, Ubuntu and Windows.

# Install

``` bash
$ pip3 install pickledir
```

# Use

### Save, read, delete

``` python3
from pickledir import PickleDir

cache = PickleDir('/tmp/my_cache')

# saving data to files
cache['a'] = 'hello, user!'
cache['b'] = 1
cache['c'] = [1, 2, 3, 4, 5]

# reading files
print(cache['a'])
print(cache['b'])
print(cache['c'])

# delete item
del cache['b']
```

### Read all values

``` python3
for key, value in cache.items():
    print(key, value)
```

### Set expiration time

``` python3    
import datetime

# setting expiration date on writing 
# (the expired items will be removed from the storage)
cache.set('x', 1000, max_age = datetime.timedelta(seconds=1))
print(cache.get('x'))  # 1000
time.sleep(2)     
print(cache.get('x'))  # None

# setting expiration date on reading
# (the expired items will not be returned)
cache['y'] = 1000
time.sleep(2)
cache.get('y' max_age = datetime.timedelta(seconds=1)) # None
cache.get('y' max_age = datetime.timedelta(seconds=10)) # 1000
```

### Set data version 

``` puthon3 
cache = PickleDir('/tmp/my_cache', version=1)
cache['a'] = 'some_data'
```

You can read all stored data while the `version` value is `1`.

``` python3 
cache = PickleDir('/tmp/my_cache', version=1)
print(cache.get('a'))  # 'some_data'
```

If you decide that all the data in the cache is out of date, just pass the 
constructor a version number that you haven't used before.

``` python3 
cache = PickleDir('/tmp/my_cache', version=2)
print(cache.get('a'))  # None
```

Now all that is saved with version 2 is actual data. Any other version is 
considered obsolete and will be gradually removed.

``` python3 
cache = PickleDir('/tmp/my_cache', version=1)
print(cache.get('a'))  # Schrödinger's data
```


# Under the hood

The implementation is deliberately naive. Each file stores a pickled dictionary
(`dict_in_file: Dict`).
`dict_in_file[key]` keeps the value of the item associated with `key`.

With a small number of items, each item is stored in a separate file (in a
dictionary with a single item). With a larger number of items, some files will
store dictionaries with multiple items. There will be a maximum of 4096 files in
total. The string keys of two items generate the same hash, the items are stored
in the same file.

This solution is extremely simple and universally compatible.

However, with a large number or size of items, disadvantages also appear.
Reading and modifying files that contain multiple items is predictably slower:
we will read and save the whole dictionary each time.



A cache for storing objects inside a file directory.

Object keys can be any string. Objects must be pickle serializable.

---

Unit-tested on macOS, Ubuntu and Windows with Python 3.7 and 3.9. 

# Install

``` bash
$ pip3 install pickledir
```

# Use

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
```

### Reading all values

``` python3
for key, value in cache.items():
    print(key, value)
```

### Expiration dates
    
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

# Under the hood

The technical solution is deliberately naive. Each file stores a pickled `dict`.
The `stored_dict[key]` keeps the value of element associated with `key`.

With small number of items, each item is stored in a separate file (in a
dictionary with single item). With a larger the number of items, some files will
store dictionaries with multiple items. Reading and modifying files that contain
multiple items is predictably slower: we will read and save the whole
dictionary each time.

There will be a maximum of 4096 files in total. The string keys of two items 
generate the same hash, the items are stored in the same file.

File-based key-value storage.

Keys can be any string. Objects must
be [pickle](https://docs.python.org/3/library/pickle.html) serializable.

---

Unit-tested with Python 3.6-3.9 on macOS, Ubuntu and Windows.

# Install

``` bash
$ pip3 install pickledir
```

# Use

## Save, read, delete

``` python3
from pickledir import PickleDir

cache = PickleDir('path/to/my_cache_dir')

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

## Read all values

``` python3
for key, value in cache.items():
    print(key, value)
```

## Set expiration time on writing

The expired items will be removed from the storage.

``` python3    
cache.set('a', 1000, max_age = datetime.timedelta(seconds=1))
print(cache.get('a'))  # 1000
time.sleep(2)     
print(cache.get('a'))  # None (and removed from storage)
```

## Set expiration time on reading

The expired items will not be returned, but kept in the storage.

``` python3
cache['b'] = 1000
time.sleep(2)
cache.get('b' max_age = datetime.timedelta(seconds=1)) # None
cache.get('b' max_age = datetime.timedelta(seconds=9)) # 1000
```

## Set data version

``` python3 
cache = PickleDir('path/to/dir', version=1)
cache['a'] = 'some_data'
```

You can read all stored data while the `version` value is `1`.

``` python3 
cache = PickleDir('path/to/dir', version=1)
print(cache.get('a'))  # 'some_data'
```

If you decide that all the data in the cache is out of date, just pass the
constructor a version number that you haven't used before.

``` python3 
cache = PickleDir('path/to/dir', version=2)
print(cache.get('a'))  # None
```

Now all that is saved with version `2` is actual data. Any other version is
considered obsolete and will be gradually removed.

Do not create the `PickleDir` with an old version number. It will make the data
unpredictable.

``` python3
cacheV1 = PickleDir('path/to/dir', version=1)  # ok
cacheV1['a'] = 'old A'
cacheV1['b'] = 'old B'

cacheV2 = PickleDir('path/to/dir', version=2)  # ok
cacheV2['a'] = 'new A'

cacheV1 = PickleDir('path/to/dir', version=1)  # don't do this
print(cacheV1.get('b'))  # Schrödinger's data ('old B' or None)
```

# Under the hood

Serialized data is stored inside files in the same directory. The maximum number
of files is limited to 4096. Each file contains one or more items.

This implementation is extremely simple and universally compatible. It has zero
initialization time. It is very fast when reading and writing, when the number
of items is small.

However, if the file contains more than one item, each read / write operation
takes longer. If there are 3 items in the file, we have to read all three, even
if only one is requested.

If we have more than 4096 items, it is absolutely certain that some of them are
adjacent in the same file. With so many items, it's worth choosing a different caching solution.
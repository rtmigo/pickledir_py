# [pickledir](https://github.com/rtmigo/pickledir_py#readme)

File-based key-value storage.

Keys and values are serialized
with [pickle](https://docs.python.org/3/library/pickle.html). Data is kept in
files in the specified directory.

CI-tested with Python 3.8-3.9 on macOS, Ubuntu and Windows.

---


The storage has zero initialization time, fast random access, fast reads and
writes.

Unlike [shelve](https://docs.python.org/3/library/shelve.html), the data saved
by PickleDir is cross-platform: you can write it on Linux and read on Windows.
Unlike most database-based caching solutions (including the shelve), the
PickleDir does not require the "open" and "close" the storage. It's always open,
since it's just a directory in the file system.

PickleDir is better for casual data storage. Database-based solutions are better
when your storage has many elements (3 thousands or more). They will also may be
faster when working with a predictably high load in terms of reading and
writing.

# Install

``` bash
$ pip3 install pickledir
```

# Use

## Create

``` python3
from pickledir import PickleDir

cache = PickleDir('path/to/my_cache_dir')
```

## Write

Keys do not need to be hashable. They only need to be serializable with `pickle`
.

When you assign a value, the data is literally written to a file.

``` python3
cache['key'] = 'hello, user!'
cache[5] = 23
cache[{'a', 'b', 'c'}] = 'abc'
```

## Read

``` python3
print(cache['key'])
print(cache[5])
print(cache[{'a', 'b', 'c'}])
```

## Read all values

``` python3 
for key, value in cache.items():
    print(key, value)
```    

## Delete item

``` python3
del cache['key']
```

## Type hints

``` python3
# declaring PickleDir with string keys and integer values:

cache: PickleDir[str, int] = PickleDir('path/to/my_cache_dir')
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

Setting the data version makes it easy to mark old data as obsolete.

For example, you cached the result of a function, and then changed the
implementation of that function. In this case, there is no need to delete old
files from the cache. Just change the version number.

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

However, if the file contains more than one item, each read/write operation
takes longer. If there are 3 items in the file, we have to read all three, even
if only one is requested.

If we have more than 4096 items, it is absolutely certain that some of them are
adjacent in the same file. With so many items, the PickleDir may be not so
efficient as database-based caches.
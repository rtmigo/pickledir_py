# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import time
import unittest
from typing import Iterable
from datetime import timedelta
from tempfile import TemporaryDirectory

from pickledir import PickleDir


def files_count(cache: PickleDir): return sum(
    1 for _ in cache.dirpath.glob('*'))


class TestCache(unittest.TestCase):

    def test_directory_not_exists(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td + "/nonexistent")
            cache['a'] = 1
            self.assertEqual(cache['a'], 1)

    def test_get_set_item(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)

            with self.assertRaises(KeyError):
                _ = cache['abc']

            cache['abc'] = 42

            self.assertEqual(cache['abc'], 42)

    def test_keys_types(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)

            cache[5] = 23
            cache[{1, 2, 3, 4, 5}] = 'the set'
            cache[[{5, 1}, {3, 4}]] = 'list with sets'

            self.assertEqual(cache[{1, 2, 3, 4, 5}], 'the set')
            self.assertEqual(cache[[{5, 1}, {3, 4}]], 'list with sets')
            self.assertEqual(cache[5], 23)

    def test_get_default(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)
            self.assertIsNone(cache.get('a'))
            self.assertEqual(cache.get('a', default=42), 42)
            cache['a'] = 777
            self.assertEqual(cache.get('a', default=42), 777)

    def test_contains(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)
            self.assertFalse('abc' in cache)
            cache['abc'] = 42
            self.assertTrue('abc' in cache)

    def test_delete(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)
            cache['a'] = 1
            cache['b'] = 2
            cache['c'] = 3
            self.assertIn('a', cache)
            self.assertIn('b', cache)
            self.assertIn('c', cache)

            del cache['b']
            self.assertIn('a', cache)
            self.assertNotIn('b', cache)
            self.assertIn('c', cache)

            del cache['a']
            self.assertNotIn('a', cache)
            self.assertNotIn('b', cache)
            self.assertIn('c', cache)

    def test_expires_on_set(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)
            with self.assertRaises(KeyError):
                _ = cache['abc']
            cache.set('abc', 777, max_age=timedelta(seconds=0.25))
            self.assertEqual(cache['abc'], 777)
            time.sleep(0.5)
            with self.assertRaises(KeyError):
                _ = cache['abc']

    def test_version_expired(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td, version=1)
            cache['a'] = 1
            cache['b'] = 2

            self.assertEqual(files_count(cache), 2)

            cache2 = PickleDir(td, version=1)
            self.assertIn('a', cache2)
            self.assertIn('b', cache2)

            cache3 = PickleDir(td, version=2)
            self.assertNotIn('a', cache3)
            self.assertNotIn('b', cache3)

            self.assertEqual(files_count(cache), 0)

            # l = list(cache.items())
            # l.sort()
            # self.assertEqual(l, [('a', 1), ('b', 249), ('c', 5)])

    def test_iter(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)
            with self.assertRaises(KeyError):
                _ = cache['abc']
            cache.set('abc', 777, max_age=timedelta(seconds=0.25))
            self.assertEqual(cache['abc'], 777)
            time.sleep(0.5)
            with self.assertRaises(KeyError):
                _ = cache['abc']

    def test_file_removed_when_expired(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)

            self.assertEqual(files_count(cache), 0)

            cache.set('never_expires', 999)
            self.assertEqual(files_count(cache), 1)

            cache.set('abc', 777, max_age=timedelta(seconds=0.5))
            self.assertTrue('abc' in cache)
            self.assertEqual(files_count(cache), 2)

            time.sleep(0.5)
            self.assertFalse('abc' in cache)
            print(list(cache.dirpath.glob('*')))
            self.assertEqual(files_count(cache), 1)

    def test_items(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)

            cache['c'] = 5
            cache['a'] = 1
            cache['b'] = 249

            l = list(cache.items())
            l.sort()
            self.assertEqual(l, [('a', 1), ('b', 249), ('c', 5)])

    def test_same_hash(self):
        k1 = 'key_one'
        same = iter(find_same_hash_keys(k1))
        next(same)
        k2 = next(same)
        k3 = next(same)
        # ['key_one', 'key2076', 'key15414', 'key16919', 'key24046']
        # self.assertEqual(PickleDir._key_to_hash(k1), PickleDir._key_to_hash(k2))
        # self.assertEqual(PickleDir._key_to_hash(k1), PickleDir._key_to_hash(k3))
        with TemporaryDirectory() as td:
            cache = PickleDir(td)

            self.assertEqual(files_count(cache), 0)
            cache[k3] = 3
            cache[k1] = 1
            cache[k2] = 2
            self.assertEqual(files_count(cache), 1)

            cache['other-hash'] = 99

            self.assertEqual(files_count(cache), 2)

            self.assertEqual(cache[k1], 1)
            self.assertEqual(cache[k2], 2)
            self.assertEqual(cache[k3], 3)

    def test_temp_files_removed_on_iteraton(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)
            cache['a'] = 1
            cache['b'] = 2
            cache['c'] = 3

            tmp = (cache.dirpath / "~labuda")
            tmp.write_text('life is short')
            self.assertTrue(tmp.exists())

            self.assertEqual(len(list(cache.items())), 3)

            self.assertFalse(tmp.exists())

    def test_other_files_ignored_on_iteraton(self):
        with TemporaryDirectory() as td:
            cache = PickleDir(td)
            cache['a'] = 1
            cache['b'] = 2
            cache['c'] = 3

            (cache.dirpath/".DS_Store").mkdir() # will also be ignored

            tmp = (cache.dirpath / "survivor")
            tmp.write_text('I will survive!')
            self.assertTrue(tmp.exists())

            self.assertEqual(len(list(cache.items())), 3)

            self.assertTrue(tmp.exists())

    def test_generic_types(self):
        with TemporaryDirectory() as td:
            cache: PickleDir[str, int] = PickleDir(td)
            cache['a'] = 1

    def test_hashes_do_not_change(self):
        self.assertEqual(key_to_hash('first'), '7a4')
        self.assertEqual(key_to_hash('second'), '68f')
        self.assertEqual(key_to_hash('third'), '09b')

    def test_our_filenames(self):
        self.assertEqual(PickleDir._is_data_basename('~12b'), True)
        self.assertEqual(PickleDir._is_data_basename('~'), True)
        self.assertEqual(PickleDir._is_data_basename('abc'), True)
        self.assertEqual(PickleDir._is_data_basename('111'), True)
        self.assertEqual(PickleDir._is_data_basename('abcd'), False)



def key_to_hash(key: object) -> str:
    return PickleDir._key_bytes_to_hash(PickleDir._key_to_bytes(key))


def find_same_hash_keys(first_key="key_one") -> Iterable[str]:
    first_key_hash = key_to_hash(first_key)
    print(first_key_hash)
    i = 0
    yield first_key
    while True:
        i += 1
        k = f"key{i}"
        # k = k[::-1]
        # print(key_to_hash(k))
        if key_to_hash(k) == first_key_hash:
            yield k


if __name__ == "__main__":
    # find_same_hash_keys()
    pass
    # find_same_hash_keys()
    # TestCache().test_get_set_item()
    # TestCache().test_file_removed_when_expired()
    # unittest.main()
    from itertools import islice

    print(list(islice(find_same_hash_keys(), 5)))
    # print()

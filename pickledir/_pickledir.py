# SPDX-FileCopyrightText: (c) 2016 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import hashlib, zlib
import os
import pickle
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import *
import warnings

from pickledir._hex import mask_4096

T = TypeVar('T')


class Record(NamedTuple):
    created: datetime
    expires: Optional[datetime]
    data: Any


class PickleDir(Generic[T]):
    """Key-value file storage for objects serializable by pickle.
    Objects are identified by arbitrary string keys.
    Optionally, each object can be associated with its expiration date.
    """

    def __init__(self, dirpath: Union[str, Path], version: int = 1):

        self.dirpath = Path(dirpath)
        self.version = version

    @staticmethod
    def _key_to_hash(key: str) -> str:
        return mask_4096(zlib.crc32(key.encode('utf-8')))

    def _key_to_file(self, key: str) -> Path:
        return self.dirpath / (self._key_to_hash(key) + ".dat")

    def _load_records(self, filepath: Path, can_write=False) -> \
            Dict[str, Record]:
        # loads a list of records a file. If an element is out of date,
        # it will be missing from the results. If canWrite = True, this will
        # also update the file removing the obsolete elements

        if not filepath.exists():
            return dict()

        with filepath.open("rb") as f:
            (version, itemsDict) = pickle.load(f)

        if version != self.version:
            os.remove(str(filepath))
            return dict()
            # problems = pickle.loadMultiple(f)

        # removing outdated items

        changed = False
        if itemsDict:
            now = self._now()
            for key, (creationTime, expirationTime, message) in tuple(
                    itemsDict.items()):
                if expirationTime and now >= expirationTime:
                    del itemsDict[key]
                    changed = True

        # if something is deleted (and modification of the file is allowed by
        # the argument), save the modified dictionary back to file

        if changed and can_write:
            if itemsDict:
                self._save_file(filepath, itemsDict)
            else:
                # no more data in this file
                os.remove(str(filepath))

        # возвращаю результат
        return itemsDict

    def _save_file(self, filepath: Path, items: Dict[str, Record]):

        if not items:
            os.remove(filepath)
            return

        if not filepath.parent.exists():
            filepath.parent.mkdir(parents=True)

        temp_filepath = filepath.parent / ("~" + filepath.name)
        assert self._is_temp_filename(temp_filepath)
        try:
            os.remove(str(temp_filepath))
        except FileNotFoundError:
            pass

        with temp_filepath.open("wb") as f:
            pickle.dump((self.version, items), f, pickle.HIGHEST_PROTOCOL)

        temp_filepath.replace(filepath)

    @staticmethod
    def _now():
        return datetime.utcnow().replace(tzinfo=timezone.utc)

    def set(self, key: str, value: T,
            max_age: timedelta = None) -> None:

        filepath = self._key_to_file(key)
        dict_in_file = self._load_records(filepath, can_write=False)

        creationTime = self._now()
        expirationTime = creationTime + max_age if max_age else None

        dict_in_file[key] = Record(creationTime, expirationTime, value)

        self._save_file(filepath, dict_in_file)

    def __delitem__(self, key: str):
        filepath = self._key_to_file(key)
        dict_in_file = self._load_records(filepath, can_write=False)
        if key in dict_in_file:
            del dict_in_file[key]
        self._save_file(filepath, dict_in_file)

    def _get_record(self, key: str, max_age: timedelta = None) \
            -> Optional[Record]:

        """
        :param key: The key.

        :param max_age: Only items younger than `max_age` will be returned.

        This is not the same as `max_age` from the `set_record`. If we use
        `max_age` in both `set_record` and `get_record`, it means the item
        must satisfy both conditions.

        But the `max_age` in `set_record` also means, that the older items
        should never be returned - and should be deleted when found. The
        `max_age` in `get_record` only filters the results of particular call.

        :return: The item (if found) or None.
        """

        path = self._key_to_file(key)

        try:
            items_dict = self._load_records(path, can_write=True)
        except FileNotFoundError:
            return None

        item = items_dict.get(key)

        if max_age is not None and item is not None:
            creationTime = item[0]
            minCreationTime = self._now() - max_age
            if creationTime < minCreationTime:
                return None

        return item

    def __getitem__(self, key: str) -> T:
        return self.get(key, default=KeyError)

    def __setitem__(self, key: str, value: T):
        return self.set(key, value=value)

    @staticmethod
    def _is_temp_filename(file: Path):
        return file.name.startswith('~')

    def get(self, key: str, max_age: timedelta = None,
            default=None) -> T:

        item = self._get_record(key, max_age)
        if item is not None:
            return item[2]
        else:
            if default == KeyError:
                raise KeyError
            else:
                return default

    def _iter_records(self) -> Iterator[Tuple[str, Tuple]]:
        for fn in self.dirpath.glob("*"):

            if self._is_temp_filename(fn):
                os.remove(str(fn))
            for key, rec in self._load_records(fn).items():
                yield key, rec

    def __contains__(self, key: str) -> bool:
        return self._get_record(key) is not None  # todo optimize

    def items(self) -> Iterator[Tuple[str, T]]:
        for url, rec in self._iter_records():
            yield url, rec[2]

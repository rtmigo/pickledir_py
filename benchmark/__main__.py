import shelve
import timeit
from collections import Callable
from tempfile import TemporaryDirectory

from pickledir import PickleDir
from diskcache import Cache

N = 10

def write_and_read(cache):
    for i in range(N):
        cache[str(i)] = {"data": i, "other": None}
    for i in range(N):
        _ = cache[str(i)]


def run_pickledir():
    with TemporaryDirectory() as td:
        cache = PickleDir(td)
        write_and_read(cache)


def run_diskcache():
    with TemporaryDirectory() as td:
        with Cache(td) as cache:
            write_and_read(cache)


def run_shelve():
    with TemporaryDirectory() as td:
        with shelve.open(td + "/file") as cache:
            write_and_read(cache)

def bench(name: str, func: Callable):
    time = timeit.timeit(
        stmt=func,
        number=100)
    print(f"{name} | {time:.2f}")


if __name__ == "__main__":
    print("Storage | Time")
    print("--------|-----")
    for _ in range(2):
        bench("PickleDir", run_pickledir)
        bench("shelve", run_shelve)
        bench("diskcache", run_diskcache)

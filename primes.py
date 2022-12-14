from pathlib import Path
from functools import cache, lru_cache

import numpy as np

NPZ_DIR = Path("npz")
NPZ_DIR.mkdir(exist_ok=True)


@cache
def get_ranges() -> dict[range, Path]:
    """Returns a dictionary of ranges and their corresponding npz files."""
    ranges = {}
    for f in NPZ_DIR.glob("*.npz"):
        start, end = f.stem.split("-")
        ranges[range(int(start), int(end) + 1)] = f
    return ranges


@cache
def n_range(n: int) -> range:
    """Returns the correct range of primes that contain n"""
    for r in get_ranges():
        if n in r:
            return r
    raise ValueError(f"{n} is not in any range")


@cache
def max_prime() -> int:
    """Returns the largest prime in the dataset"""
    return max(get_ranges().keys(), key=lambda r: r.stop).stop


@lru_cache(maxsize=5)  # Currently limited to 5 * (~100 MB each) ~= 500 MB of memory
def load_primes(r: range) -> np.ndarray:
    """Loads the primes in the given range from the npz file"""
    file_path = get_ranges()[r]
    print("Loading from", file_path)  # TODO: Switch to logging
    return np.load(file_path)["primes"]


@lru_cache(maxsize=512)
# TODO: Turn this to an API call
def is_prime(n: int) -> bool:
    """Returns True if n is prime, False otherwise. Raises ValueError if n is not in our dataset"""
    if n < 2:
        return False
    elif n > max_prime():
        if str(n)[-1] in "024568":
            return False
        else:
            raise ValueError(f"{n} is too large for our data")
    else:
        try:
            r = n_range(n)
        except ValueError:
            return False
        else:
            primes = load_primes(r)
            return n == primes[np.searchsorted(primes, n)]


@lru_cache(maxsize=512)
# TODO: Turn this to an API call
def prime_range(start: int, end: int = 0, count: int = 100) -> list:
    """Returns a list of primes between start and end (inclusive) with a maximum of length of count"""
    end = end + 1 if end else max_prime() + 1
    results = []
    for i in range(start, end):
        if is_prime(i):
            results.append(i)
            if len(results) == count:
                break
    return results


@lru_cache(maxsize=512)
# TODO: Turn this to an API call
# TODO: Get global index and not just the range index
def prime_index(n: int) -> int:
    """Returns the index of the prime in the prime range that contains n"""
    if is_prime(n):
        r = n_range(n)
        primes = load_primes(r)
        return np.searchsorted(primes, n)
    else:
        return -1


@lru_cache(maxsize=512)
# TODO: Turn this to an API call
# TODO: Make this work
def prime_by_index(i: int) -> int:
    """Returns the prime at the given index among all primes in the dataset"""
    pass


def main():  # TODO: remove test code
    print(prime_range(1, 100))
    check_across_sets = prime_range(179424670, count=10)
    print(check_across_sets, len(check_across_sets))
    for n in (1, 2, 101, 179424672, 373587883, 373587882, 5112733750, max_prime() + 1):
        try:
            print(n, is_prime(n))
            print(n, "Index:", prime_index(n))
        except ValueError as e:
            print(n, e)


if __name__ == "__main__":
    main()

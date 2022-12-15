from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path

import numpy as np

NPZ_DIR = Path("npz")
NPZ_DIR.mkdir(exist_ok=True)  # todo: this is a hack, should be in a setup script
PRIMES_PER_FILE = 10_000_000  # todo: need to verify this or normalize the files
CACHE_SIZE = 5  # Number of npz files to keep in memory, 5 * ~100MB ~= 500MB RAM


@dataclass
class PrimeRange:
    start: int
    end: int
    path: Path
    index: int = 0

    def __contains__(self, item: int) -> bool:
        return self.start <= item <= self.end

    def __repr__(self) -> str:
        return f"PrimeRange<{self.start}-{self.end} ({self.index})>"

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __eq__(self, other) -> bool:
        return self.start == other.start and self.end == other.end

    @lru_cache(maxsize=CACHE_SIZE)
    def primes(self) -> np.ndarray:
        print("Loading from", self.path)  # TODO: Switch to logging
        return np.load(self.path)["primes"]

    def prime_index(self, n: int) -> tuple[bool, int]:
        if n not in self:
            raise ValueError(f"Error: {n} is not in {self.start}<=>{self.end}")
        primes = self.primes()
        index = np.searchsorted(primes, n)
        is_prime = primes[index] == n
        return (is_prime, self.index * PRIMES_PER_FILE + index + 1)

    @classmethod
    def from_file(cls, f: Path):
        start, end = f.stem.split("-")
        return cls(int(start), int(end) + 1, f)


@lru_cache(maxsize=512)
def is_prime_compute(n: int) -> bool:
    """Returns whether n is prime, computing it without the dataset."""
    for i in range(2, int(np.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


@cache
def get_ranges() -> list[PrimeRange]:
    """Returns sorted PrimeRange objects based on files."""
    ranges = [PrimeRange.from_file(f) for f in NPZ_DIR.glob("*.npz")]
    ranges = sorted(ranges, key=lambda r: r.start)
    for i, r in enumerate(ranges):
        r.index = i
    return ranges


@lru_cache(maxsize=CACHE_SIZE)
def range_index(n: int) -> int:
    """Returns the index of the range that (might) contain n"""
    prime_ranges = get_ranges()
    all_ends = [r.end for r in prime_ranges]
    return np.searchsorted(all_ends, n)


@cache
def max_prime() -> int:
    return get_ranges()[-1].end - 1


MAX_PRIME = max_prime()

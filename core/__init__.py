from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path

import numpy as np

NPZ_DIR = Path("npz")
NPZ_DIR.mkdir(exist_ok=True)
CACHE_SIZE = 5  # Number of npz files to keep in memory, 5 * ~100MB ~= 500MB RAM


@dataclass
class PrimeRange:
    start: int
    end: int
    path: Path
    index: int = 0

    def __contains__(self, item: int) -> bool:
        return self.start <= item <= self.end

    @lru_cache(maxsize=CACHE_SIZE)
    def primes(self) -> np.ndarray:
        print("Loading from", self.path)  # TODO: Switch to logging
        return np.load(self.path)["primes"]

    @classmethod
    def from_file(cls, f: Path):
        start, end = f.stem.split("-")
        return cls(int(start), int(end) + 1, f)


@cache
def get_ranges() -> list[PrimeRange]:
    """Returns sorted PrimeRange objects based on files."""
    ranges = [PrimeRange.from_file(f) for f in NPZ_DIR.glob("*.npz")]
    ranges = sorted(ranges, key=lambda r: r.start)
    for i, r in enumerate(ranges):
        r.index = i
    return ranges


@lru_cache(maxsize=CACHE_SIZE)
def n_range(n: int) -> PrimeRange | None:
    """Returns the correct range of primes that (might) contain n"""
    prime_ranges = get_ranges()
    all_ends = [r.end for r in prime_ranges]
    return np.searchsorted(all_ends, n)


@cache
def max_prime() -> int:
    return get_ranges()[-1].end - 1

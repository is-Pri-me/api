import os
from dataclasses import dataclass
from functools import cache, lru_cache
from io import BytesIO
from pathlib import Path

import boto3
import numpy as np
from dotenv import load_dotenv

load_dotenv(override=True)

PRIMES_PER_FILE = 10_000_000  # todo: need to verify this or normalize the files
CACHE_SIZE = 5  # Number of npz files to keep in memory, 5 * ~100MB ~= 500MB RAM

NPZ_ACCESS_KEY = os.getenv("NPZ_ACCESS_KEY")
NPZ_SECRET_KEY = os.getenv("NPZ_SECRET_KEY")
NPZ_BUCKET_NAME = os.getenv("NPZ_BUCKET_NAME")
NPZ_ENDPOINT_URL = os.getenv("NPZ_ENDPOINT_URL")

if not all((NPZ_ACCESS_KEY, NPZ_SECRET_KEY, NPZ_BUCKET_NAME, NPZ_ENDPOINT_URL)):
    raise ValueError("NPZ credentials not set")
else:
    S3 = boto3.resource(
        "s3",
        aws_access_key_id=NPZ_ACCESS_KEY,
        aws_secret_access_key=NPZ_SECRET_KEY,
        endpoint_url=NPZ_ENDPOINT_URL,
    )
    BUCKET = S3.Bucket(NPZ_BUCKET_NAME)
    NPZ_LIST = [o.key for o in BUCKET.objects.all() if o.key.endswith(".npz")]


@dataclass
class PrimeRange:
    start: int
    end: int
    npz_filename: str = None
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
        print("Loading from", self.npz_filename)  # TODO: Switch to logging
        body = BUCKET.Object(self.npz_filename).get()["Body"]
        bytes_obj = BytesIO(body.read())
        return np.load(bytes_obj)["primes"]

    def prime_index(self, n: int) -> tuple[bool, int]:
        if n not in self:
            raise ValueError(f"Error: {n} is not in {self.start}<=>{self.end}")
        primes = self.primes()
        index = np.searchsorted(primes, n)
        is_prime = primes[index] == n
        return (is_prime, self.index * PRIMES_PER_FILE + index + 1)

    @classmethod
    def from_filename(cls, f: str):
        """Load an npz file from the bucket."""
        start, end = Path(f).stem.split("-")
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
    print("Loading ranges from S3")  # TODO: Switch to logging
    ranges = [PrimeRange.from_filename(f) for f in NPZ_LIST]
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

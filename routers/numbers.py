import numpy as np
from fastapi import APIRouter
from numpy import random

from core import MAX_PRIME, PRIMES_PER_FILE, get_ranges, range_index
from errors import IndexTooSmall, NumberTooLarge, NumberTooSmall, RangeTooLarge, UnknownError
from models import BaseNumber, PrimeRangeResponse

router = APIRouter(
    tags=["Numbers"],
)


@router.get("/random", description="Returns a random prime number")
async def get_random() -> BaseNumber:
    ranges = get_ranges()
    random_range = random.choice(ranges)
    primes = random_range.primes()
    random_index = random.randint(0, len(primes))
    random_prime = primes[random_index]
    absolute_index = random_index + random_range.index * PRIMES_PER_FILE
    return BaseNumber(number=random_prime, is_prime=True, prime_index=absolute_index)


@router.get("/max", description="Returns the largest prime we have")
async def get_max() -> BaseNumber:
    last_range = get_ranges()[-1]
    max_index = last_range.index * PRIMES_PER_FILE + len(last_range.primes()) - 1
    return BaseNumber(number=MAX_PRIME, is_prime=True, prime_index=max_index)


@router.get("/{number}", description="Returns whether the number is prime")
async def get_number(number: int) -> BaseNumber:
    if number < 2:
        raise NumberTooSmall(number)
    elif number > MAX_PRIME:
        if str(number)[-1] in "024568":
            return BaseNumber(number=number, is_prime=False)
        else:
            raise NumberTooLarge(number)
    else:
        prime_range = get_ranges()[range_index(number)]
        try:
            is_prime, index = prime_range.prime_index(number)
            index = index if is_prime else None
            return BaseNumber(number=number, is_prime=is_prime, prime_index=index)
        except ValueError:
            pass
    raise UnknownError(f"Unable to find {number} in our dataset (r:{prime_range}))")


@router.get("/index/{index}", description="Returns the prime number at the given index")
def prime_index(index: int) -> BaseNumber:
    # TODO: This is just a placeholder, it's not correct
    if index < 0:
        raise IndexTooSmall()
    elif index > MAX_PRIME:  # todo: This is wrong, should be max index
        raise NumberTooLarge(index)
    else:
        prime_range = get_ranges()[range_index(index)]
        try:
            prime = prime_range.prime_at_index(index)
            return BaseNumber(number=prime, is_prime=True, prime_index=index)
        except ValueError:
            pass


@router.get("/primes_in_range", description="Returns a list of prime numbers")
def get_primes_in_range(start: int, limit: int) -> PrimeRangeResponse:
    RANGE_LIMIT = 100

    if start < 2:
        start = 2
    if start > MAX_PRIME:
        raise NumberTooLarge(start)
    if limit > RANGE_LIMIT:
        raise RangeTooLarge(RANGE_LIMIT)

    ranges = get_ranges()
    start_primes = ranges[range_index(start)].primes()
    first_index = np.searchsorted(start_primes, start)
    end_index = first_index + limit
    result = start_primes[first_index:end_index].tolist()
    if len(result) < limit:
        next_primes = ranges[range_index(start + 1)].primes()
        limit_missing = limit - len(result)
        result += next_primes[:limit_missing].tolist()
    return PrimeRangeResponse(start=start, limit=limit, primes=result)

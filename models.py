from pydantic import BaseModel


class BaseNumber(BaseModel):
    number: int
    is_prime: bool
    prime_index: int | None = None


class PrimeRangeResponse(BaseModel):
    start: int
    limit: int
    primes: list[int]

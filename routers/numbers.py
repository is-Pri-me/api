from fastapi import APIRouter

from core import max_prime, prime_index
from errors import InvalidRange, NumberTooLarge, NumberTooSmall
from models import BaseNumber

MAX_PRIME = max_prime()

router = APIRouter(
    tags=["Numbers"],
)


@router.get("/max_prime", description="Returns the largest prime we have")
async def get_max_prime() -> BaseNumber:
    return BaseNumber(number=MAX_PRIME, is_prime=True)


@router.get("/{number}", description="Returns whether the number is prime")
async def get_number(number: int) -> BaseNumber:
    if number < 2:
        raise NumberTooSmall(number)
    if number > await max_prime():
        raise NumberTooLarge(number)
    result = await prime_index(number)
    return BaseNumber(number=number, is_prime=result)


# @router.get(
#     "/range/{start}/{end}",
#     description="Returns a list of primes between start and end (inclusive)",
# )
# async def prime_range(start: int, end: int = 0, count: int = 100) -> list[BaseNumber]:
#     if start < 2:
#         start = 2
#         if start > await max_prime():
#             raise NumberTooLarge(start)
#     if end and end < start:
#         raise InvalidRange(start, end)
#     end = end + 1 if end else max_prime() + 1
#     results = []
#     for i in range(start, end):
#         result = await is_prime(i)
#         if result:
#             results.append(i)
#             if len(results) == count:
#                 break
#     return results

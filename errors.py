from fastapi import HTTPException, status

from core import MAX_PRIME


class UnknownError(HTTPException):
    def __init__(self, error: str):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, error)


class NumberTooLarge(HTTPException):
    def __init__(self, number: int):
        error = f"{number} is too large, out dataset ends at {MAX_PRIME})"
        super().__init__(status.HTTP_406_NOT_ACCEPTABLE, error)


class NumberTooSmall(HTTPException):
    def __init__(self, number: int):
        error = f"{number} is too small, prime numbers start at 2"
        super().__init__(status.HTTP_406_NOT_ACCEPTABLE, error)


class RangeTooLarge(HTTPException):
    def __init__(self, limit: int):
        error = f"Range too large, must be less than {limit}"
        super().__init__(status.HTTP_406_NOT_ACCEPTABLE, error)

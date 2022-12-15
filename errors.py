from fastapi import HTTPException, status


class NumberTooLarge(HTTPException):
    def __init__(self, number: int):
        error = f"{number} is too large, not in our dataset"
        super().__init__(status.HTTP_406_NOT_ACCEPTABLE, error)


class NumberTooSmall(HTTPException):
    def __init__(self, number: int):
        error = f"{number} is too small, prime numbers start at 2"
        super().__init__(status.HTTP_406_NOT_ACCEPTABLE, error)


class InvalidRange(HTTPException):
    def __init__(self, start: int, end: int):
        error = f"Invalid range ({start} {end}), start must be less than end"
        super().__init__(status.HTTP_406_NOT_ACCEPTABLE, error)

from pydantic import BaseModel


class BaseNumber(BaseModel):
    number: int
    is_prime: bool

from fastapi import FastAPI, HTTPException
from primes import is_prime

app = FastAPI()


@app.get("/")
async def index():
    return {"hello": "world"}


@app.get("/healthcheck")
async def healthcheck():
    return {"result": "ok"}


@app.get("/{number}")
async def get_number(number: int):
    result = await is_prime(number)
    return {"number": number, "is_prime": result}


@app.get("/error/")
async def error():
    raise HTTPException(400, detail="Not authorized")

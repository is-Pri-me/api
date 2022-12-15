from routers import numbers
from fastapi import FastAPI

app = FastAPI()
app.include_router(numbers.router)


@app.get("/health_check")
async def health_check():
    return {"result": "ok"}

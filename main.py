from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q, "mode": "synchronous"}



@app.get("/a/")
async def read_root():
    return {"Hello": "Asynchronous World"}


@app.get("/a/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q, "mode": "asynchronous"}



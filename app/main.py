from fastapi import FastAPI
from routes import books, movies

app = FastAPI(title="Media Catalog", version="1.0.0")

app.include_router(books.router)
app.include_router(movies.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
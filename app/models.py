from pydantic import BaseModel

class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    year: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: str

class MovieBase(BaseModel):
    title: str
    director: str
    genre: str
    year: int

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: str
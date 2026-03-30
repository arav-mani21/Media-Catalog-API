from fastapi import APIRouter, HTTPException
from models import Book, BookCreate
import database as db
import uuid

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", status_code=201)
def create_book(book: BookCreate):
    item = book.model_dump()
    item["id"] = str(uuid.uuid4())
    db.put_book(item)
    return Book(**item)

@router.get("/")
def get_all_books():
    all_books = db.get_all_books()
    return [Book.model_validate(book) for book in all_books]

@router.get("/{id}")
def get_book(id: str):
    book = db.get_book(id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return Book.model_validate(book)

@router.put("/{id}")
def update_book(id: str, updates: dict):
    if db.get_book(id) is None:
        raise HTTPException(status_code=404, detail="Book not found")
    updated_book = db.update_book(id, updates)
    return Book.model_validate(updated_book)

@router.delete("/{id}")
def delete_book(id: str):
    book = db.get_book(id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete_book(id)
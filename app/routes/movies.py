from fastapi import APIRouter, HTTPException
from models import Movie, MovieCreate
import database as db
import uuid

router = APIRouter(prefix="/movies", tags=["movies"])

@router.post("/", status_code=201)
def create_movie(movie: MovieCreate):
    item = movie.model_dump()
    item["id"] = str(uuid.uuid4())
    db.put_movie(item)
    return Movie(**item)

@router.get("/")
def get_all_movies():
    all_movies = db.get_all_movies()
    return [Movie.model_validate(movie) for movie in all_movies]

@router.get("/{id}")
def get_movie(id: str):
    movie = db.get_movie(id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return Movie.model_validate(movie)

@router.put("/{id}")
def update_movie(id: str, updates: dict):
    if db.get_movie(id) is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    updated_movie = db.update_movie(id, updates)
    return Movie.model_validate(updated_movie)

@router.delete("/{id}")
def delete_movie(id: str):
    movie = db.get_movie(id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete_movie(id)
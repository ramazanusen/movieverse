from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import os
from datetime import datetime

app = FastAPI(title="Movieverse API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class Movie(BaseModel):
    id: int
    title: str
    overview: str
    release_date: str
    vote_average: float
    poster_path: Optional[str] = None
    genres: List[str]

# Mock data - In production, this would come from a database
MOVIES_FILE = "data/movies.json"

def load_movies():
    try:
        if os.path.exists(MOVIES_FILE):
            with open(MOVIES_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading movies: {e}")
        return []

# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Movieverse API"}

@app.get("/api/movies", response_model=List[Movie])
async def get_movies():
    movies = load_movies()
    return movies

@app.get("/api/movies/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    movies = load_movies()
    movie = next((m for m in movies if m["id"] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get("/api/movies/search/{query}")
async def search_movies(query: str):
    movies = load_movies()
    query = query.lower()
    results = [
        movie for movie in movies
        if query in movie["title"].lower() or query in movie["overview"].lower()
    ]
    return results

@app.get("/api/movies/genre/{genre}")
async def get_movies_by_genre(genre: str):
    movies = load_movies()
    genre = genre.lower()
    results = [
        movie for movie in movies
        if genre in [g.lower() for g in movie["genres"]]
    ]
    return results

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)

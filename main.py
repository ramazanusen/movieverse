from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Movieverse API",
    version="1.0.0",
    description="A Netflix-style movie analytics platform"
)

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
            logger.info(f"Loading movies from {MOVIES_FILE}")
            with open(MOVIES_FILE, "r") as f:
                return json.load(f)
        logger.warning(f"Movies file not found at {MOVIES_FILE}")
        return []
    except Exception as e:
        logger.error(f"Error loading movies: {str(e)}")
        return []

# API Routes
@app.get("/")
async def root():
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "message": "Welcome to Movieverse API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/movies", response_model=List[Movie])
async def get_movies():
    logger.info("Fetching all movies")
    movies = load_movies()
    logger.info(f"Found {len(movies)} movies")
    return movies

@app.get("/api/movies/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    logger.info(f"Fetching movie with id {movie_id}")
    movies = load_movies()
    movie = next((m for m in movies if m["id"] == movie_id), None)
    if not movie:
        logger.warning(f"Movie with id {movie_id} not found")
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get("/api/movies/search/{query}")
async def search_movies(query: str):
    logger.info(f"Searching movies with query: {query}")
    movies = load_movies()
    query = query.lower()
    results = [
        movie for movie in movies
        if query in movie["title"].lower() or query in movie["overview"].lower()
    ]
    logger.info(f"Found {len(results)} movies matching query: {query}")
    return results

@app.get("/api/movies/genre/{genre}")
async def get_movies_by_genre(genre: str):
    logger.info(f"Fetching movies by genre: {genre}")
    movies = load_movies()
    genre = genre.lower()
    results = [
        movie for movie in movies
        if genre in [g.lower() for g in movie["genres"]]
    ]
    logger.info(f"Found {len(results)} movies in genre: {genre}")
    return results

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

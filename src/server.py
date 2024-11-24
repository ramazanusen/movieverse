from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.ingestion.imdb_collector import IMDBCollector

app = FastAPI(title="Movie Analytics Platform")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize collector
data_dir = os.getenv("IMDB_DATA_DIR", "data")
collector = IMDBCollector(data_dir=data_dir)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# API routes
@app.get("/api")
async def root():
    return {"message": "Movie Analytics Platform API"}

@app.get("/api/movies")
async def get_movies(
    limit: int = Query(10, ge=1, le=100),
    genres: Optional[List[str]] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=10),
    min_votes: Optional[int] = Query(None, ge=0),
    language: Optional[str] = Query(None),
    year_from: Optional[int] = Query(None, ge=1900),
    year_to: Optional[int] = Query(None, le=2024)
):
    try:
        if language:
            return collector.get_movies_by_language(language, limit)
        elif genres:
            return collector.get_movies_by_genres(genres, limit=limit)
        else:
            return collector.get_movies_with_filters(
                genres=genres,
                min_rating=min_rating,
                min_votes=min_votes,
                min_year=year_from,
                max_year=year_to,
                limit=limit
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/genres")
async def get_genres():
    return collector.get_available_genres()

@app.get("/api/languages")
async def get_languages():
    return collector.get_available_languages()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

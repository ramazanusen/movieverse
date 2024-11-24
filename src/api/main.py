from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.ingestion.imdb_collector import IMDBCollector

app = FastAPI(title="Movie Analytics Platform API")
logger = logging.getLogger(__name__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize collector
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
logger.info(f"Using data directory: {data_dir}")
collector = IMDBCollector(data_dir=data_dir)

@app.get("/")
async def root():
    return {"message": "Movie Analytics Platform API"}

@app.get("/movies")
async def get_movies(
    limit: int = Query(10, ge=1, le=100),
    genres: Optional[List[str]] = Query(None),
    min_rating: Optional[float] = Query(5.0, ge=0, le=10),
    min_votes: Optional[int] = Query(100, ge=0),
    year_from: Optional[int] = Query(None, ge=1900),
    year_to: Optional[int] = Query(None, le=2024)
):
    """Get movies with filters"""
    try:
        logger.info(f"Getting movies with params: limit={limit}, genres={genres}, min_rating={min_rating}, "
                   f"min_votes={min_votes}, year_from={year_from}, year_to={year_to}")
        
        # Use the get_movies_with_filters method directly
        movies = collector.get_movies_with_filters(
            genres=genres,
            min_rating=min_rating,
            min_votes=min_votes,
            min_year=year_from,
            max_year=year_to,
            limit=limit
        )
        
        logger.info(f"Returning {len(movies)} movies")
        if len(movies) > 0:
            logger.info(f"Sample movie: {movies[0]}")
        return movies
        
    except Exception as e:
        logger.error(f"Error in get_movies endpoint: {str(e)}")
        logger.exception("Detailed traceback:")
        return []

@app.get("/genres")
async def get_genres():
    """Get available genres with their movie counts"""
    return collector.get_available_genres()

@app.get("/languages")
async def get_languages():
    """Get available languages with their movie counts"""
    return collector.get_available_languages()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

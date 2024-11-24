"""
Module for using operating system dependent functionality.

If not otherwise specified, many of the functions and types in this module
return or refer to strings containing a path. Paths are represented as
strings, and the returned path will only contain Unicode characters in
case the system supports it.

References:
  - https://docs.python.org/3/library/os.html

"""

import os
import logging
from typing import Dict, List, Optional
import tmdbsimple as tmdb
from datetime import datetime, timedelta
import pandas as pd
from ..utils.logger import setup_logger
from ..models.schema import MovieSchema

logger = setup_logger(__name__)

class TMDBCollector:
    """
    Collector class for fetching movie data from TMDB API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize TMDB collector with API key."""
        self.api_key = api_key or os.getenv('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError("TMDB API key is required")
        
        tmdb.API_KEY = self.api_key
        self.movies = tmdb.Movies()
        
    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Fetch popular movies from TMDB."""
        try:
            response = self.movies.popular(page=page)
            return response['results']
        except Exception as e:
            logger.error(f"Error fetching popular movies: {str(e)}")
            return []
            
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Fetch detailed information for a specific movie."""
        try:
            movie = tmdb.Movies(movie_id)
            details = movie.info()
            credits = movie.credits()
            keywords = movie.keywords()
            
            # Combine all information
            details['cast'] = credits.get('cast', [])[:5]  # Top 5 cast members
            details['crew'] = credits.get('crew', [])[:5]  # Top 5 crew members
            details['keywords'] = keywords.get('keywords', [])
            
            return details
        except Exception as e:
            logger.error(f"Error fetching movie details for ID {movie_id}: {str(e)}")
            return None
            
    def get_recent_movies(self, days: int = 7) -> List[Dict]:
        """Fetch movies released in the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            response = self.movies.discover(
                primary_release_date_gte=start_date.strftime('%Y-%m-%d'),
                primary_release_date_lte=end_date.strftime('%Y-%m-%d')
            )
            return response['results']
        except Exception as e:
            logger.error(f"Error fetching recent movies: {str(e)}")
            return []
            
    def collect_and_transform(self, num_pages: int = 5) -> pd.DataFrame:
        """Collect movie data and transform it into a DataFrame."""
        all_movies = []
        
        # Collect popular movies
        for page in range(1, num_pages + 1):
            movies = self.get_popular_movies(page=page)
            for movie in movies:
                details = self.get_movie_details(movie['id'])
                if details:
                    all_movies.append(details)
                    
        # Transform to DataFrame
        df = pd.DataFrame(all_movies)
        
        # Apply schema
        schema = MovieSchema()
        df = schema.apply(df)
        
        return df
        
    def save_to_csv(self, df: pd.DataFrame, output_path: str):
        """Save the collected data to a CSV file."""
        try:
            df.to_csv(output_path, index=False)
            logger.info(f"Successfully saved data to {output_path}")
        except Exception as e:
            logger.error(f"Error saving data to CSV: {str(e)}")
            
if __name__ == "__main__":
    # Example usage
    collector = TMDBCollector()
    df = collector.collect_and_transform(num_pages=2)
    collector.save_to_csv(df, "tmdb_movies.csv")
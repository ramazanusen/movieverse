import os
import logging
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime
from ..utils.logger import setup_logger
from ..models.schema import MovieSchema

logger = setup_logger(__name__)

class IMDBCollector:
    """
    Collector class for processing IMDB dataset files.
    Expects the following files:
    - title.basics.tsv: Basic movie information
    - title.ratings.tsv: Movie ratings
    - title.akas.tsv: Alternative titles and languages
    """
    
    def __init__(self, data_dir: str):
        """
        Initialize IMDB collector.
        
        Args:
            data_dir: Directory containing IMDB dataset files
        """
        self.data_dir = data_dir
        self._load_datasets()
        
    def _load_datasets(self):
        """Load and prepare IMDB datasets."""
        logger.info(f"Loading IMDB datasets from directory: {self.data_dir}")
        
        try:
            # Load basics with selected columns
            basics_path = os.path.join(self.data_dir, 'title.basics.tsv')
            logger.info(f"Loading basics from {basics_path}")
            if not os.path.exists(basics_path):
                raise FileNotFoundError(f"File not found: {basics_path}")
                
            self.basics_df = pd.read_csv(
                basics_path, 
                sep='\t',
                usecols=['tconst', 'titleType', 'primaryTitle', 'originalTitle', 
                        'startYear', 'runtimeMinutes', 'genres'],
                dtype={
                    'tconst': str,
                    'titleType': str,
                    'primaryTitle': str,
                    'originalTitle': str,
                    'startYear': str,
                    'runtimeMinutes': str,
                    'genres': str
                }
            )
            
            # Filter for movies only
            logger.info(f"Total rows in basics before movie filter: {len(self.basics_df)}")
            self.basics_df = self.basics_df[self.basics_df['titleType'] == 'movie']
            logger.info(f"Movies after type filtering: {len(self.basics_df)}")
            logger.info(f"Sample movie data: {self.basics_df.head(1).to_dict('records')}")
            
            # Load ratings
            ratings_path = os.path.join(self.data_dir, 'title.ratings.tsv')
            logger.info(f"Loading ratings from {ratings_path}")
            if not os.path.exists(ratings_path):
                raise FileNotFoundError(f"File not found: {ratings_path}")
                
            self.ratings_df = pd.read_csv(
                ratings_path,
                sep='\t',
                dtype={
                    'tconst': str,
                    'averageRating': float,
                    'numVotes': int
                }
            )
            logger.info(f"Total ratings loaded: {len(self.ratings_df)}")
            logger.info(f"Sample rating data: {self.ratings_df.head(1).to_dict('records')}")
            
            # Verify data integrity
            movies_with_ratings = pd.merge(self.basics_df, self.ratings_df, on='tconst', how='inner')
            logger.info(f"Total movies with ratings: {len(movies_with_ratings)}")
            logger.info(f"Sample merged data: {movies_with_ratings.head(1).to_dict('records')}")
            
        except Exception as e:
            logger.error(f"Error loading datasets: {str(e)}")
            logger.exception("Detailed traceback:")
            raise
            
    def _get_movie_language(self, movie_id: str) -> str:
        """Get the primary language of a movie."""
        try:
            # Read the file in chunks to avoid memory issues
            chunk_size = 10000
            with open(os.path.join(self.data_dir, 'title.akas.tsv'), 'r', encoding='utf-8') as f:
                # Skip header
                next(f)
                
                while True:
                    chunk = pd.read_csv(f, sep='\t', nrows=chunk_size, names=[
                        'titleId', 'ordering', 'title', 'region', 'language', 'types',
                        'attributes', 'isOriginalTitle'
                    ])
                    
                    if chunk.empty:
                        break
                    
                    # Filter for the specific movie
                    movie_entries = chunk[chunk['titleId'] == movie_id]
                    
                    if not movie_entries.empty:
                        # Try to get language from original title first
                        original_title = movie_entries[movie_entries['isOriginalTitle'] == 1]
                        if not original_title.empty and pd.notna(original_title.iloc[0]['language']):
                            return original_title.iloc[0]['language']
                        
                        # Fallback to most common language
                        languages = movie_entries['language'].dropna()
                        if not languages.empty:
                            return languages.mode().iloc[0]
            
            return 'unknown'
        except Exception as e:
            logger.error(f"Error getting movie language: {str(e)}")
            return 'unknown'
            
    def get_top_movies(self, limit: int = 250) -> List[Dict]:
        """Get top rated movies based on rating and number of votes."""
        try:
            logger.info(f"Getting top {limit} movies...")
            
            # Merge basics with ratings
            df = pd.merge(self.basics_df, self.ratings_df, left_on='tconst', right_on='tconst')
            
            # Filter movies with significant number of votes (e.g., top 20%)
            vote_threshold = df['numVotes'].quantile(0.8)
            df = df[df['numVotes'] >= vote_threshold]
            
            # Sort by rating and get top movies
            top_movies = df.sort_values('averageRating', ascending=False).head(limit)
            
            return [self._movie_to_dict(row) for _, row in top_movies.iterrows()]
        except Exception as e:
            logger.error(f"Error getting top movies: {str(e)}")
            return []
            
    def get_popular_movies(self, limit: int = 100, min_year: Optional[str] = None) -> List[Dict]:
        """Get popular movies based on number of votes, optionally filtered by year."""
        try:
            logger.info(f"Getting {limit} popular movies...")
            
            # Merge basics with ratings
            df = pd.merge(self.basics_df, self.ratings_df, left_on='tconst', right_on='tconst')
            
            # Apply year filter if specified
            if min_year:
                df = df[df['startYear'].astype(str).str.isnumeric()]
                df = df[df['startYear'].astype(int) >= int(min_year)]
            
            # Sort by number of votes and get top movies
            popular_movies = df.sort_values('numVotes', ascending=False).head(limit)
            
            return [self._movie_to_dict(row) for _, row in popular_movies.iterrows()]
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            return []
            
    def search_movies(self, query: str, limit: int = 10, filter_genre: bool = True) -> List[Dict]:
        """Search for movies by title or genre."""
        try:
            logger.info(f"Searching for movies with query: {query}")
            
            # Search in titles and genres
            title_mask = (
                self.basics_df['primaryTitle'].str.contains(query, case=False, na=False) |
                self.basics_df['originalTitle'].str.contains(query, case=False, na=False)
            )
            
            genre_mask = self.basics_df['genres'].str.contains(query, case=False, na=False) if filter_genre else False
            
            matches = pd.merge(
                self.basics_df[title_mask | genre_mask],
                self.ratings_df,
                on='tconst',
                how='left'
            ).sort_values('numVotes', ascending=False).head(limit)
            
            return [self._movie_to_dict(row) for _, row in matches.iterrows()]
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            return []
            
    def get_movies_by_language(self, language_code: str, limit: int = 10) -> List[Dict]:
        """Get movies by their primary language."""
        try:
            logger.info(f"Getting movies in language: {language_code}")
            
            # Get movie IDs for the specified language
            movie_ids = [
                movie_id for movie_id in self.basics_df['tconst']
                if self._get_movie_language(movie_id) == language_code
            ]
            
            # Get movies and their ratings
            movies_df = pd.merge(
                self.basics_df[self.basics_df['tconst'].isin(movie_ids)],
                self.ratings_df,
                on='tconst',
                how='left'
            ).sort_values('numVotes', ascending=False).head(limit)
            
            return [self._movie_to_dict(row) for _, row in movies_df.iterrows()]
        except Exception as e:
            logger.error(f"Error getting movies by language: {str(e)}")
            return []
    
    def get_available_languages(self) -> List[Dict[str, Union[str, int]]]:
        """Get a list of available languages and their movie counts."""
        try:
            languages = {}
            for movie_id in self.basics_df['tconst']:
                language = self._get_movie_language(movie_id)
                if language not in languages:
                    languages[language] = 0
                languages[language] += 1
            
            return [
                {"code": lang, "count": count}
                for lang, count in languages.items()
                if lang and lang != 'unknown'
            ]
        except Exception as e:
            logger.error(f"Error getting available languages: {str(e)}")
            return []
            
    def _movie_to_dict(self, row: pd.Series) -> Dict:
        """Convert a movie row to a dictionary."""
        try:
            movie_dict = {
                'id': row['tconst'],
                'title': row['primaryTitle'],
                'originalTitle': row['originalTitle'],
                'year': int(row['startYear']) if pd.notna(row['startYear']) and row['startYear'] != '\\N' else None,
                'runtime': int(row['runtimeMinutes']) if pd.notna(row['runtimeMinutes']) and row['runtimeMinutes'] != '\\N' else None,
                'genres': row['genres'].split(',') if pd.notna(row['genres']) else [],
                'averageRating': float(row['averageRating']) if 'averageRating' in row and pd.notna(row['averageRating']) else None,
                'numVotes': int(row['numVotes']) if 'numVotes' in row and pd.notna(row['numVotes']) else 0
            }
            
            # Add language if available
            movie_dict['language'] = self._get_movie_language(row['tconst'])
            
            return movie_dict
        except Exception as e:
            logger.error(f"Error converting movie to dict: {str(e)}")
            return {
                'id': row['tconst'],
                'title': row['primaryTitle'],
                'error': str(e)
            }
            
    def collect_and_transform(self, num_movies: int = 100) -> pd.DataFrame:
        """Collect movie data and transform it into a DataFrame."""
        try:
            logger.info(f"Collecting {num_movies} movies...")
            
            # Get both popular and top-rated movies
            popular_movies = self.get_popular_movies(limit=num_movies // 2)
            top_movies = self.get_top_movies(limit=num_movies // 2)
            
            # Combine and remove duplicates
            all_movies = []
            seen_ids = set()
            
            for movie in popular_movies + top_movies:
                if movie and movie['id'] not in seen_ids:
                    all_movies.append(movie)
                    seen_ids.add(movie['id'])
            
            logger.info(f"Collected {len(all_movies)} unique movies")
            
            # Create DataFrame
            df = pd.DataFrame(all_movies)
            
            # Apply schema
            schema = MovieSchema()
            df = schema.apply(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error collecting and transforming movies: {str(e)}")
            return pd.DataFrame()
            
    def save_to_csv(self, df: pd.DataFrame, output_path: str):
        """Save the collected data to a CSV file."""
        try:
            df.to_csv(output_path, index=False)
            logger.info(f"Successfully saved data to {output_path}")
        except Exception as e:
            logger.error(f"Error saving data to CSV: {str(e)}")
            
    def get_movies_by_genres(self, genres: List[str], match_all: bool = True, limit: int = 10) -> List[Dict]:
        """
        Get movies by genres. Can match all genres or any genre.
        
        Args:
            genres: List of genres to match
            match_all: If True, movies must have all specified genres. If False, movies can have any of the genres.
            limit: Maximum number of movies to return
        """
        try:
            logger.info(f"Getting movies with genres: {genres}")
            
            # Convert genres to lowercase for case-insensitive matching
            genres = [g.lower() for g in genres]
            
            # Filter movies based on genres
            def has_genres(genre_str):
                if pd.isna(genre_str):
                    return False
                movie_genres = [g.lower() for g in genre_str.split(',')]
                if match_all:
                    return all(g in movie_genres for g in genres)
                else:
                    return any(g in movie_genres for g in genres)
            
            # Apply genre filter
            genre_mask = self.basics_df['genres'].apply(has_genres)
            matches = pd.merge(
                self.basics_df[genre_mask],
                self.ratings_df,
                on='tconst',
                how='left'
            ).sort_values('numVotes', ascending=False).head(limit)
            
            return [self._movie_to_dict(row) for _, row in matches.iterrows()]
        except Exception as e:
            logger.error(f"Error getting movies by genres: {str(e)}")
            return []
    
    def get_available_genres(self) -> List[Dict[str, int]]:
        """Get a list of all available genres and their counts."""
        try:
            genre_counts = {}
            
            # Collect all genres and their counts
            for genres_str in self.basics_df['genres'].dropna():
                for genre in genres_str.split(','):
                    genre = genre.strip()
                    if genre not in genre_counts:
                        genre_counts[genre] = 0
                    genre_counts[genre] += 1
            
            return [
                {"name": genre, "count": count}
                for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
            ]
        except Exception as e:
            logger.error(f"Error getting available genres: {str(e)}")
            return []
    
    def get_movies_with_filters(self, 
                              genres: Optional[List[str]] = None,
                              min_rating: float = 5.0,  
                              min_votes: int = 100,  
                              min_year: Optional[int] = None,
                              max_year: Optional[int] = None,
                              min_runtime: Optional[int] = None,
                              max_runtime: Optional[int] = None,
                              limit: int = 10) -> List[Dict]:
        """
        Get movies with multiple filters.
        
        Args:
            genres: List of genres (must match all)
            min_rating: Minimum rating (0-10)
            min_votes: Minimum number of votes
            min_year: Minimum release year
            max_year: Maximum release year
            min_runtime: Minimum runtime in minutes
            max_runtime: Maximum runtime in minutes
            limit: Maximum number of movies to return
        """
        try:
            logger.info(f"Getting movies with filters: genres={genres}, min_rating={min_rating}, "
                       f"min_votes={min_votes}, min_year={min_year}, max_year={max_year}, "
                       f"min_runtime={min_runtime}, max_runtime={max_runtime}, limit={limit}")
            
            # Start with ratings filter as it's usually the most restrictive
            logger.info("Merging basics with ratings...")
            df = pd.merge(self.basics_df, self.ratings_df, on='tconst', how='inner')
            logger.info(f"Initial merge resulted in {len(df)} movies")
            
            # Filter for movies only
            df = df[df['titleType'] == 'movie']
            logger.info(f"After movie type filter: {len(df)} movies")
            
            # Apply rating and vote filters
            logger.info("Applying rating and vote filters...")
            df = df[
                (df['averageRating'] >= min_rating) &
                (df['numVotes'] >= min_votes)
            ]
            logger.info(f"After rating/vote filters: {len(df)} movies")
            if len(df) > 0:
                logger.info(f"Sample movie after filters: {df.iloc[0].to_dict()}")
            
            # Apply year filter if specified
            if min_year is not None or max_year is not None:
                logger.info("Applying year filters...")
                df['year'] = pd.to_numeric(df['startYear'].replace('\\N', pd.NA), errors='coerce')
                if min_year is not None:
                    df = df[df['year'] >= min_year]
                if max_year is not None:
                    df = df[df['year'] <= max_year]
                logger.info(f"After year filters: {len(df)} movies")
            
            # Apply runtime filter if specified
            if min_runtime is not None or max_runtime is not None:
                logger.info("Applying runtime filters...")
                df['runtime'] = pd.to_numeric(df['runtimeMinutes'].replace('\\N', pd.NA), errors='coerce')
                if min_runtime is not None:
                    df = df[df['runtime'] >= min_runtime]
                if max_runtime is not None:
                    df = df[df['runtime'] <= max_runtime]
                logger.info(f"After runtime filters: {len(df)} movies")
            
            # Apply genre filter if specified
            if genres:
                logger.info("Applying genre filters...")
                genres = [g.lower() for g in genres]
                df = df[df['genres'].apply(lambda x: 
                    any(g in [g.lower() for g in str(x).split(',')] for g in genres)  
                    if pd.notna(x) else False
                )]
                logger.info(f"After genre filters: {len(df)} movies")
            
            # Sort by rating and number of votes
            logger.info("Sorting movies...")
            df = df.sort_values(['averageRating', 'numVotes'], ascending=[False, False])
            
            # Get top movies
            movies = df.head(limit)
            logger.info(f"Selected top {len(movies)} movies")
            
            # Convert to list of dictionaries
            result = []
            for _, row in movies.iterrows():
                try:
                    movie_dict = {
                        'id': row['tconst'],
                        'title': row['primaryTitle'],
                        'year': int(row['startYear']) if row['startYear'] != '\\N' else None,
                        'rating': float(row['averageRating']),
                        'votes': int(row['numVotes']),
                        'genres': row['genres'].split(',') if pd.notna(row['genres']) else [],
                        'runtime': int(row['runtimeMinutes']) if row['runtimeMinutes'] != '\\N' else None
                    }
                    result.append(movie_dict)
                except Exception as e:
                    logger.error(f"Error converting movie {row['tconst']} to dict: {str(e)}")
            
            logger.info(f"Final result: {len(result)} movies")
            if len(result) > 0:
                logger.info(f"Sample movie: {result[0]}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting filtered movies: {str(e)}")
            logger.exception("Detailed traceback:")
            return []
            
if __name__ == "__main__":
    # Example usage
    collector = IMDBCollector(data_dir='path_to_your_imdb_dataset')
    df = collector.collect_and_transform(num_movies=10)
    collector.save_to_csv(df, "imdb_movies.csv")
import os
import sys
import pandas as pd

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.imdb_collector import IMDBCollector

def test_imdb_collector():
    # Initialize the collector with the data directory
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    collector = IMDBCollector(data_dir)
    
    print("\nTesting IMDBCollector initialization and data loading...")
    
    # Test getting top movies
    print("\nTesting get_top_movies()...")
    top_movies = collector.get_top_movies(limit=5)
    print(f"Top 5 movies by rating:")
    for movie in top_movies:
        print(f"- {movie['title']} (Rating: {movie['vote_average']}, Votes: {movie['vote_count']})")
    
    # Test getting popular movies
    print("\nTesting get_popular_movies()...")
    popular_movies = collector.get_popular_movies(limit=5)
    print(f"Top 5 popular movies by votes:")
    for movie in popular_movies:
        print(f"- {movie['title']} (Votes: {movie['vote_count']}, Rating: {movie['vote_average']})")
    
    # Test searching movies
    search_query = "Matrix"
    print(f"\nTesting search_movies() with query '{search_query}'...")
    search_results = collector.search_movies(search_query, limit=5)
    print(f"Search results for '{search_query}':")
    for movie in search_results:
        if movie:  # Check if movie is not None
            print(f"- {movie['title']} ({movie.get('release_date', 'N/A')})")
    
    # Test collecting and transforming data
    print("\nTesting collect_and_transform()...")
    transformed_data = collector.collect_and_transform(num_movies=5)
    print("Sample of transformed data:")
    print(transformed_data.head())

if __name__ == "__main__":
    test_imdb_collector()

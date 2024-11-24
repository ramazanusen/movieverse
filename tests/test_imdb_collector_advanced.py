import os
import sys
import pandas as pd

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.imdb_collector import IMDBCollector

def test_genre_specific_movies():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    collector = IMDBCollector(data_dir)
    
    # Test searching for specific genres
    print("\nTesting genre-specific movies...")
    search_results = collector.search_movies("Action", limit=5, filter_genre=True)
    print("Action movies (by genre):")
    for movie in search_results:
        if movie:
            genres = ", ".join([g["name"] for g in movie["genres"]])
            print(f"- {movie['title']} ({movie.get('release_date', 'N/A')}) - Genres: {genres}")

def test_foreign_language_movies():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    collector = IMDBCollector(data_dir)
    
    # Test searching for foreign language films
    print("\nTesting foreign language movies...")
    search_results = collector.search_movies("Leben", limit=5)  # German word for "life"
    print("German movies:")
    for movie in search_results:
        if movie:
            print(f"- {movie['title']} ({movie.get('release_date', 'N/A')}) - Language: {movie['original_language']}")

def test_recent_popular_movies():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    collector = IMDBCollector(data_dir)
    
    # Get recent popular movies
    print("\nTesting recent popular movies...")
    popular_movies = collector.get_popular_movies(limit=10, min_year="2020")
    print("Recent popular movies (2020 onwards):")
    for movie in popular_movies:
        if movie:
            print(f"- {movie['title']} ({movie.get('release_date', 'N/A')}) - "
                  f"Rating: {movie['vote_average']}, Votes: {movie['vote_count']}")

def test_runtime_analysis():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    collector = IMDBCollector(data_dir)
    
    # Get popular movies and analyze their runtimes
    print("\nTesting movie runtime analysis...")
    popular_movies = collector.get_popular_movies(limit=10)
    print("Popular movies with runtime:")
    for movie in popular_movies:
        if movie:
            hours = movie['runtime'] // 60
            minutes = movie['runtime'] % 60
            runtime_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            print(f"- {movie['title']} - Runtime: {runtime_str}")

if __name__ == "__main__":
    print("Running advanced IMDB Collector tests...")
    
    print("\n=== Testing Genre-Specific Movies ===")
    test_genre_specific_movies()
    
    print("\n=== Testing Foreign Language Movies ===")
    test_foreign_language_movies()
    
    print("\n=== Testing Recent Popular Movies ===")
    test_recent_popular_movies()
    
    print("\n=== Testing Runtime Analysis ===")
    test_runtime_analysis()

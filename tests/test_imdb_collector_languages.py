import os
import sys
import pandas as pd

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.imdb_collector import IMDBCollector

def test_language_features():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    collector = IMDBCollector(data_dir)
    
    # Test getting movies in specific languages
    test_languages = ['fr', 'de', 'es', 'ja']  # French, German, Spanish, Japanese
    
    for lang_code in test_languages:
        print(f"\nTesting movies in {lang_code}...")
        movies = collector.get_movies_by_language(lang_code, limit=3)  # Reduced limit for faster testing
        print(f"Top 3 {lang_code} movies by popularity:")
        for movie in movies:
            if movie:
                print(f"- {movie['title']} ({movie.get('release_date', 'N/A')}) - "
                      f"Rating: {movie['vote_average']}, Votes: {movie['vote_count']}")

if __name__ == "__main__":
    print("Running IMDB Collector language tests...")
    test_language_features()

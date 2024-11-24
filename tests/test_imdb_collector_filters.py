import unittest
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ingestion.imdb_collector import IMDBCollector

class TestIMDBCollectorFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Assuming IMDB dataset is in a 'data' directory at project root
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        cls.collector = IMDBCollector(data_dir=data_dir)
    
    def test_get_movies_by_genres(self):
        # Test with single genre
        action_movies = self.collector.get_movies_by_genres(['Action'], limit=5)
        self.assertTrue(len(action_movies) > 0)
        
        # Test with multiple genres (match_all=True)
        action_drama = self.collector.get_movies_by_genres(['Action', 'Drama'], match_all=True, limit=5)
        self.assertTrue(len(action_drama) > 0)
        
        # Test with multiple genres (match_all=False)
        action_or_drama = self.collector.get_movies_by_genres(['Action', 'Drama'], match_all=False, limit=5)
        self.assertTrue(len(action_or_drama) > 0)
    
    def test_get_available_genres(self):
        genres = self.collector.get_available_genres()
        self.assertTrue(len(genres) > 0)
        self.assertTrue(all('name' in g and 'count' in g for g in genres))
    
    def test_get_movies_with_filters(self):
        # Test with rating and vote filters
        top_rated = self.collector.get_movies_with_filters(
            min_rating=8.0,
            min_votes=10000,
            limit=5
        )
        self.assertTrue(len(top_rated) > 0)
        self.assertTrue(all(m['averageRating'] >= 8.0 for m in top_rated))
        
        # Test with year range
        modern_movies = self.collector.get_movies_with_filters(
            min_year=2020,
            min_votes=1000,
            limit=5
        )
        self.assertTrue(len(modern_movies) > 0)
        
        # Test with runtime range
        long_movies = self.collector.get_movies_with_filters(
            min_runtime=180,  # 3 hours or longer
            min_votes=1000,
            limit=5
        )
        self.assertTrue(len(long_movies) > 0)
        
        # Test with combined filters
        filtered_movies = self.collector.get_movies_with_filters(
            genres=['Drama'],
            min_rating=7.5,
            min_votes=5000,
            min_year=2010,
            max_year=2023,
            min_runtime=90,
            max_runtime=180,
            limit=5
        )
        self.assertTrue(len(filtered_movies) > 0)

if __name__ == '__main__':
    unittest.main()

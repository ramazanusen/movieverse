import pytest
from unittest.mock import Mock, patch
import pandas as pd
from src.ingestion.tmdb_collector import TMDBCollector

@pytest.fixture
def mock_tmdb_response():
    return {
        'results': [
            {
                'id': 1,
                'title': 'Test Movie',
                'overview': 'Test Overview',
                'release_date': '2024-01-01',
                'vote_average': 7.5
            }
        ]
    }

@pytest.fixture
def mock_movie_details():
    return {
        'id': 1,
        'title': 'Test Movie',
        'overview': 'Test Overview',
        'release_date': '2024-01-01',
        'vote_average': 7.5,
        'runtime': 120,
        'budget': 1000000,
        'revenue': 5000000,
        'genres': [{'id': 1, 'name': 'Action'}],
        'production_companies': [{'id': 1, 'name': 'Test Studio'}]
    }

@pytest.fixture
def mock_tmdb(mock_tmdb_response, mock_movie_details):
    mock = Mock()
    # Mock Movies class
    mock_movies = Mock()
    mock_movies.popular.return_value = mock_tmdb_response
    mock_movies.discover.return_value = mock_tmdb_response
    mock_movies.info.return_value = mock_movie_details
    mock_movies.credits.return_value = {'cast': [], 'crew': []}
    mock_movies.keywords.return_value = {'keywords': []}
    
    # Mock Movies constructor
    mock.Movies = Mock(return_value=mock_movies)
    
    return mock

@pytest.fixture
def tmdb_collector():
    with patch.dict('os.environ', {'TMDB_API_KEY': 'test_key'}):
        return TMDBCollector()

def test_init_without_api_key():
    with pytest.raises(ValueError):
        TMDBCollector(api_key=None)

def test_init_with_api_key():
    collector = TMDBCollector(api_key='test_key')
    assert collector.api_key == 'test_key'

@patch('src.ingestion.tmdb_collector.tmdb')
def test_get_popular_movies(mock_tmdb_module, mock_tmdb, tmdb_collector):
    # Replace the tmdb module with our mock
    mock_tmdb_module.Movies = mock_tmdb.Movies
    mock_tmdb_module.API_KEY = 'test_key'
    
    # Create a new collector to use our mocked tmdb module
    tmdb_collector.movies = mock_tmdb.Movies()
    
    movies = tmdb_collector.get_popular_movies()
    assert len(movies) == 1
    assert movies[0]['title'] == 'Test Movie'

@patch('src.ingestion.tmdb_collector.tmdb')
def test_get_movie_details(mock_tmdb_module, mock_tmdb, tmdb_collector):
    # Replace the tmdb module with our mock
    mock_tmdb_module.Movies = mock_tmdb.Movies
    mock_tmdb_module.API_KEY = 'test_key'
    
    details = tmdb_collector.get_movie_details(1)
    assert details is not None
    assert details['title'] == 'Test Movie'
    assert details['runtime'] == 120

@patch('src.ingestion.tmdb_collector.tmdb')
def test_get_recent_movies(mock_tmdb_module, mock_tmdb, tmdb_collector):
    # Replace the tmdb module with our mock
    mock_tmdb_module.Movies = mock_tmdb.Movies
    mock_tmdb_module.API_KEY = 'test_key'
    
    # Create a new collector to use our mocked tmdb module
    tmdb_collector.movies = mock_tmdb.Movies()
    
    movies = tmdb_collector.get_recent_movies(days=7)
    assert len(movies) == 1
    assert movies[0]['title'] == 'Test Movie'

@patch('src.ingestion.tmdb_collector.TMDBCollector.get_popular_movies')
@patch('src.ingestion.tmdb_collector.TMDBCollector.get_movie_details')
def test_collect_and_transform(mock_details, mock_popular, tmdb_collector, mock_movie_details):
    # Set up mocks to return proper data
    mock_popular.return_value = [{'id': 1, 'title': 'Test Movie'}]
    mock_details.return_value = mock_movie_details
    
    # Create a mock schema that doesn't actually transform the data
    with patch('src.models.schema.MovieSchema.apply') as mock_apply:
        mock_apply.return_value = pd.DataFrame([mock_movie_details])
        df = tmdb_collector.collect_and_transform(num_pages=1)
        
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'title' in df.columns
    assert df.iloc[0]['title'] == 'Test Movie'

def test_save_to_csv(tmdb_collector, tmp_path):
    df = pd.DataFrame({
        'title': ['Test Movie'],
        'overview': ['Test Overview']
    })
    output_path = tmp_path / "test_movies.csv"
    tmdb_collector.save_to_csv(df, str(output_path))
    assert output_path.exists()
    saved_df = pd.read_csv(str(output_path))
    assert not saved_df.empty
    assert saved_df.iloc[0]['title'] == 'Test Movie'

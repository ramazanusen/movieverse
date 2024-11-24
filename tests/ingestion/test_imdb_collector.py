import pytest
from unittest.mock import Mock, patch
import pandas as pd
from src.ingestion.imdb_collector import IMDBCollector

@pytest.fixture
def mock_movie_basic():
    movie = Mock()
    movie.getID.return_value = 'tt0111161'
    movie.data = {
        'title': 'Test Movie',
        'year': 2024,
        'kind': 'movie'
    }
    movie.get = movie.data.get
    return movie

@pytest.fixture
def mock_movie_detailed():
    movie = Mock()
    movie.getID.return_value = 'tt0111161'
    movie.data = {
        'title': 'Test Movie',
        'year': 2024,
        'rating': 8.5,
        'votes': 1000000,
        'plot': ['A test movie about testing.'],
        'runtimes': ['142'],
        'genres': ['Drama', 'Test'],
        'countries': ['USA'],
        'languages': ['English'],
        'directors': [{'name': 'Test Director'}],
        'cast': [{'name': 'Actor 1'}, {'name': 'Actor 2'}],
        'writers': [{'name': 'Test Writer'}],
        'budget': '$1000000',
        'opening weekend': '$500000',
        'gross': '$5000000',
        'keywords': ['test', 'movie', 'drama'],
        'awards': ['Test Award 2024']
    }
    movie.get = movie.data.get
    return movie

@pytest.fixture
def mock_imdb(mock_movie_basic, mock_movie_detailed):
    mock = Mock()
    
    # Mock basic movie lists
    mock.get_top250_movies.return_value = [mock_movie_basic]
    mock.get_popular100_movies.return_value = [mock_movie_basic]
    mock.search_movie.return_value = [mock_movie_basic]
    
    # Mock movie details
    mock.get_movie.return_value = mock_movie_detailed
    mock.update.return_value = None
    
    return mock

@pytest.fixture
def imdb_collector():
    return IMDBCollector()

def test_init():
    collector = IMDBCollector()
    assert hasattr(collector, 'ia')

@patch('src.ingestion.imdb_collector.IMDb')
def test_get_top_movies(mock_imdb_class, mock_imdb, imdb_collector):
    mock_imdb_class.return_value = mock_imdb
    imdb_collector.ia = mock_imdb
    
    movies = imdb_collector.get_top_movies(limit=1)
    assert len(movies) == 1
    assert movies[0]['title'] == 'Test Movie'
    assert movies[0]['imdb_id'] == 'tt0111161'

@patch('src.ingestion.imdb_collector.IMDb')
def test_get_movie_details(mock_imdb_class, mock_imdb, imdb_collector):
    mock_imdb_class.return_value = mock_imdb
    imdb_collector.ia = mock_imdb
    
    details = imdb_collector.get_movie_details('tt0111161')
    assert details is not None
    assert details['title'] == 'Test Movie'
    assert details['rating'] == 8.5
    assert len(details['cast']) == 2
    assert details['imdb_id'] == 'tt0111161'

@patch('src.ingestion.imdb_collector.IMDb')
def test_search_movies(mock_imdb_class, mock_imdb, imdb_collector):
    mock_imdb_class.return_value = mock_imdb
    imdb_collector.ia = mock_imdb
    
    movies = imdb_collector.search_movies('test', limit=1)
    assert len(movies) == 1
    assert movies[0]['title'] == 'Test Movie'
    assert movies[0]['imdb_id'] == 'tt0111161'

@patch('src.ingestion.imdb_collector.IMDb')
def test_get_popular_movies(mock_imdb_class, mock_imdb, imdb_collector):
    mock_imdb_class.return_value = mock_imdb
    imdb_collector.ia = mock_imdb
    
    movies = imdb_collector.get_popular_movies(limit=1)
    assert len(movies) == 1
    assert movies[0]['title'] == 'Test Movie'
    assert movies[0]['imdb_id'] == 'tt0111161'

@patch('src.ingestion.imdb_collector.IMDb')
def test_collect_and_transform(mock_imdb_class, mock_imdb, imdb_collector):
    mock_imdb_class.return_value = mock_imdb
    imdb_collector.ia = mock_imdb
    
    # Create a mock schema that doesn't actually transform the data
    with patch('src.models.schema.MovieSchema.apply') as mock_apply:
        mock_apply.return_value = pd.DataFrame([{
            'title': 'Test Movie',
            'imdb_id': 'tt0111161',
            'rating': 8.5
        }])
        
        df = imdb_collector.collect_and_transform(num_movies=2)
        
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'title' in df.columns
    assert df.iloc[0]['title'] == 'Test Movie'

def test_save_to_csv(imdb_collector, tmp_path):
    df = pd.DataFrame({
        'title': ['Test Movie'],
        'imdb_id': ['tt0111161']
    })
    output_path = tmp_path / "test_movies.csv"
    imdb_collector.save_to_csv(df, str(output_path))
    assert output_path.exists()
    saved_df = pd.read_csv(str(output_path))
    assert not saved_df.empty
    assert saved_df.iloc[0]['title'] == 'Test Movie'

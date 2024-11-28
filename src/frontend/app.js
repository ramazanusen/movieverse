// Debug logging
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('Error:', msg, '\nURL:', url, '\nLine:', lineNo, '\nColumn:', columnNo, '\nError object:', error);
    return false;
};

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function MovieCard({ movie }) {
    return (
        <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg transition-transform transform hover:scale-105">
            {movie.poster_path && (
                <img 
                    src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                    alt={movie.title}
                    className="w-full h-64 object-cover"
                />
            )}
            <div className="p-4">
                <h3 className="text-xl font-bold mb-2">{movie.title}</h3>
                <p className="text-gray-400 mb-2">
                    {new Date(movie.release_date).getFullYear()}
                </p>
                <div className="flex items-center mb-2">
                    <span className="text-yellow-400 mr-1">★</span>
                    <span>{movie.vote_average.toFixed(1)}</span>
                </div>
                <p className="text-gray-300 text-sm mb-4 line-clamp-3">{movie.overview}</p>
                <div className="flex flex-wrap gap-2">
                    {movie.genres.map((genre, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-600 rounded-full text-sm">
                            {genre}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}

function SearchBar({ onSearch }) {
    const [query, setQuery] = React.useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch(query);
    };

    return (
        <form onSubmit={handleSubmit} className="mb-8">
            <div className="flex gap-2">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search movies..."
                    className="flex-1 p-2 rounded bg-gray-700 text-white"
                />
                <button type="submit" className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">
                    Search
                </button>
            </div>
        </form>
    );
}

function App() {
    const [movies, setMovies] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    const fetchMovies = async (searchQuery = '') => {
        setLoading(true);
        try {
            const url = searchQuery
                ? `${API_URL}/api/movies/search/${encodeURIComponent(searchQuery)}`
                : `${API_URL}/api/movies`;
            
            console.log('Fetching movies from:', url);
            const res = await fetch(url);
            
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            
            const data = await res.json();
            console.log('Received data:', data);
            setMovies(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error('Error fetching movies:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        fetchMovies();
    }, []);

    if (error) {
        return (
            <div className="min-h-screen p-8">
                <h1 className="text-3xl font-bold mb-8">Movieverse</h1>
                <div className="bg-red-800 p-4 rounded">
                    <p>Error: {error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen p-8">
            <h1 className="text-3xl font-bold mb-8">Movieverse</h1>
            <SearchBar onSearch={fetchMovies} />
            {loading ? (
                <div className="text-center">Loading movies...</div>
            ) : movies.length === 0 ? (
                <div className="text-center">No movies found</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {movies.map((movie) => (
                        <MovieCard key={movie.id} movie={movie} />
                    ))}
                </div>
            )}
        </div>
    );
}

// Debug rendering
console.log('Rendering App component');
ReactDOM.render(<App />, document.getElementById('root'));

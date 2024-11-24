// Debug logging
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('Error:', msg, '\nURL:', url, '\nLine:', lineNo, '\nColumn:', columnNo, '\nError object:', error);
    return false;
};

const API_URL = 'http://localhost:8001';

function MovieCard({ movie }) {
    const rating = movie.rating ? movie.rating.toFixed(1) : 'N/A';
    const votes = movie.votes ? movie.votes.toLocaleString() : '0';
    const genres = Array.isArray(movie.genres) ? movie.genres : [];
    
    return (
        <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg transition-transform transform hover:scale-105">
            <div className="p-4">
                <h3 className="text-xl font-bold mb-2">{movie.title || 'Untitled'}</h3>
                <p className="text-gray-400 mb-2">
                    {movie.year ? `Year: ${movie.year}` : ''} 
                    {movie.runtime ? ` • ${movie.runtime} min` : ''}
                </p>
                <div className="flex items-center mb-2">
                    <span className="text-yellow-400 mr-1">★</span>
                    <span>{rating}</span>
                    <span className="text-gray-400 ml-2">({votes} votes)</span>
                </div>
                <div className="flex flex-wrap gap-2">
                    {genres.map((genre, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-600 rounded-full text-sm">
                            {genre}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}

function App() {
    const [movies, setMovies] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    React.useEffect(() => {
        console.log('Fetching movies from:', `${API_URL}/movies`);
        fetch(`${API_URL}/movies?limit=20&min_rating=5.0&min_votes=100`)
            .then(res => {
                console.log('Response status:', res.status);
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                console.log('Received data:', data);
                setMovies(Array.isArray(data) ? data : []);
                setLoading(false);
            })
            .catch(err => {
                console.error('Error fetching movies:', err);
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (error) {
        return (
            <div className="min-h-screen p-8">
                <h1 className="text-3xl font-bold mb-8">Movie Analytics Platform</h1>
                <div className="bg-red-800 p-4 rounded">
                    <p>Error: {error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen p-8">
            <h1 className="text-3xl font-bold mb-8">Movie Analytics Platform</h1>
            {loading ? (
                <div className="text-center">Loading movies...</div>
            ) : movies.length === 0 ? (
                <div className="text-center">No movies found</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {movies.map((movie, index) => (
                        <MovieCard key={movie.id || index} movie={movie} />
                    ))}
                </div>
            )}
        </div>
    );
}

// Debug rendering
console.log('Rendering App component');
ReactDOM.render(<App />, document.getElementById('root'));

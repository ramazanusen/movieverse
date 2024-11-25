import React, { useState, useEffect } from 'react';

function App() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(process.env.REACT_APP_API_URL + '/movies')
      .then(response => response.json())
      .then(data => {
        setMovies(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-white"></div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen flex items-center justify-center text-red-500">
      Error: {error}
    </div>
  );

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">Movieverse</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {movies.map(movie => (
          <div key={movie.id} className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
            <div className="p-4">
              <h2 className="text-xl font-semibold mb-2">{movie.title}</h2>
              <p className="text-gray-400">{movie.release_date}</p>
              <div className="mt-4 flex justify-between items-center">
                <span className="bg-blue-500 px-2 py-1 rounded text-sm">
                  {movie.vote_average} ★
                </span>
                <span className="text-gray-400 text-sm">
                  {movie.vote_count} votes
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

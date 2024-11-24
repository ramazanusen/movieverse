# Netflix-Style Movie Analytics Platform

A modern web application that displays and analyzes movie data from the IMDB dataset, featuring a FastAPI backend and React frontend.

## Features

- Browse and search movies from IMDB dataset
- Filter movies by:
  - Rating
  - Number of votes
  - Year
  - Genres
  - Runtime
- Modern, responsive UI with movie cards
- Real-time data filtering and sorting

## Tech Stack

- **Backend**:
  - FastAPI (Python web framework)
  - Pandas (Data processing)
  - Uvicorn (ASGI server)

- **Frontend**:
  - React
  - Tailwind CSS
  - Modern JavaScript (ES6+)

## Project Structure

```
src/
├── api/              # FastAPI backend
├── frontend/         # React frontend
├── ingestion/        # Data processing
├── models/          # Data models
└── utils/           # Helper utilities

data/               # IMDB dataset files
```

## Prerequisites

- Python 3.8+
- Node.js and npm (for frontend development)
- IMDB Dataset files:
  - title.basics.tsv
  - title.ratings.tsv
  - title.akas.tsv

## Setup Instructions

1. Clone the repository
```bash
git clone <repository-url>
cd netflix-style-movie-analytics
```

2. Set up the backend
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. Download IMDB dataset files
- Place the following files in the `data/` directory:
  - title.basics.tsv
  - title.ratings.tsv
  - title.akas.tsv

4. Start the backend server
```bash
python -m uvicorn src.api.main:app --reload --port 8001
```

5. Start the frontend (in a new terminal)
```bash
# Navigate to frontend directory
cd src/frontend

# Install dependencies
npm install

# Start development server
npm start
```

The application will be available at:
- Frontend: http://localhost:3002
- Backend API: http://localhost:8001

## Environment Variables

Copy `.env.example` to `.env` and configure:
```
# API Configuration
PORT=8001
HOST=localhost

# Data Directory
IMDB_DATA_DIR=./data
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
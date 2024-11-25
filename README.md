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

## Deployment

This project uses automated CI/CD pipelines with GitHub Actions:

### Continuous Integration (CI)
- Automated testing on Python 3.8 and 3.9
- Code style checking with flake8
- Code coverage reporting
- Frontend build verification

### Continuous Deployment (CD)
- Backend automatically deploys to Render.com
- Frontend automatically deploys to Vercel
- Deployments trigger on pushes to main branch

Live URLs:
- Frontend: [Vercel App URL]
- Backend API: [Render App URL]

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Create a Pull Request
4. CI checks will run automatically
5. Once approved and merged, CD will deploy your changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.
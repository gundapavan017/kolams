# Kolam Analyzer and Generator

A full-stack mini project for analyzing South Indian kolam designs and generating new kolam variations.

## Features

- Upload a kolam image and detect design rules.
- Extract dot count, grid size, symmetry, loop count, stroke type, and likely pattern family.
- Recreate the detected kolam and generate variations.
- Generate custom Flower, Star, Pulli, Lotus, Sikku, and Rangoli kolams.
- Browse a generated gallery of all supported patterns.

## Project Structure

```text
kolam-project/
  backend/    FastAPI image-analysis and generation API
  frontend/   React + Vite user interface
```

## Requirements

- Python 3.10+
- Node.js 18+

## Run Backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open the backend health check at `http://127.0.0.1:8000/`.

## Run Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000/`. The Vite dev server proxies `/api` requests to the backend at port 8000.

## API Endpoints

- `GET /` health check
- `POST /api/analyze` upload an image and receive rules, recreation, and variations
- `POST /api/generate` generate a kolam from `{ pattern, color, size }`
- `GET /api/gallery` generate gallery images
- `GET /api/patterns` list supported patterns

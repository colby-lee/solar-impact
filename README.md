# SolarImpact

SolarImpact is a full-stack MVP project that collects, stores, and visualizes NASA Solar Flare (DONKI/FLR) data.  
It uses a FastAPI backend, a React frontend, RabbitMQ for asynchronous collection triggers, and Prometheus/Grafana for metrics.

## Features
- Fetch solar flare data from NASA DONKI API
- Store flares in PostgreSQL
- Trigger new data collection on demand (via API or frontend)
- View and sort flare records in the React UI
- Expose Prometheus metrics for monitoring
- Ready for CI/CD with GitHub Actions + Heroku deployment

## Project Structure
backend/                  # FastAPI + data collector
  api/                    # API endpoints
  common/                 # DB models, utils
  data_collector/         # RabbitMQ worker + NASA client
  requirements.txt        # Python dependencies
frontend/solar-impact-frontend/
  src/                    # React components and services
  public/                 # Static assets

## Prerequisites
- Python 3.10+
- Node.js 18+ and npm or yarn
- PostgreSQL
- RabbitMQ
- (Optional) Prometheus + Grafana

## Setup

### Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload

Runs at: http://127.0.0.1:8000

### Frontend
cd frontend/solar-impact-frontend
npm install      # or yarn install
npm start        # or yarn start

Runs at: http://localhost:3000

## Data Collection
The data collector listens to RabbitMQ messages on `data_collection_queue`.

Trigger manually via the API:
curl -X POST http://127.0.0.1:8000/api/start-data-collection \
     -H "Content-Type: application/json" \
     -d '{"start_date":"2024-01-01T00:00:00Z","end_date":"2024-12-31T23:59:59Z"}'

## Testing
cd backend
pytest -v

## Monitoring
- Prometheus metrics exposed at: http://localhost:8001/
- Configure Prometheus with `prometheus.yml` and connect Grafana for dashboards.

## Deployment
1. Push to GitHub 
2. GitHub Actions runs pytest
3. Deploy to Heroku

## License
MIT


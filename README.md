# Sales Dashboard - App Feature

This branch adds a small FastAPI app and a digital world clock feature.

Endpoints added:
- GET /health — simple health check
- GET /metrics — sample aggregation from data/sample_sales.csv
- GET /clock — HTML page that displays current time in multiple time zones

How to run locally:

1. Create a virtualenv and install requirements:

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Run the app:

   uvicorn app.main:app --reload

3. Open http://localhost:8000/clock to see the digital clock.

Docker:

   docker build -t sales-dashboard .
   docker run -p 8000:8000 sales-dashboard


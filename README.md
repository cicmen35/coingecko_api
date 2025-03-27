# CoinGecko API cryptocurrency manager

## Overview
A robust FastAPI application for managing cryptocurrency data with real-time updates from CoinGecko.

## Features
- Real-time cryptocurrency data management
- CoinGecko API integration
- Background data refresh
- CRUD operations
- Streamlit UI for easy interaction

## Prerequisites
- Python 3.10
- PostgreSQL
- pip

## Installation
1. Clone the repository
2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up database
```bash
# Configure your PostgreSQL database in .env
createdb coingecko_api
```

## Running the Application

### API Server
```bash
python run.py
```
The API will be available at `http://localhost:8000`

### Streamlit UI
```bash
streamlit run streamlit_app.py
```
The Streamlit UI will open in your default web browser

## Testing
```bash
pytest tests/
```

## License
MIT License

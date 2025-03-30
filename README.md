# Coingecko api manager

## Overview
FastAPI application for managing cryptocurrency data in database with real-time updates from CoinGecko.

## Prerequisites
- Python 3.10+
- PostgreSQL
- pip

## Installation
Clone the repository
```bash
git clone https://github.com/cicmen35/coingecko_api.git
cd coingecko_api
```

## Running the Application
To set up the environment and start the application, use the provided shell script:
```bash
./start_app.sh
```

This script will:
- Create and activate a virtual environment
- Install required dependencies
- Set up the PostgreSQL database
- Start the application with:
  - FastAPI server at `http://localhost:8000`
  - Streamlit UI at `http://localhost:8501`

## Project Structure
- `app/`: FastAPI application logic
- `ui/`: Streamlit user interface
- `requirements.txt`: Project dependencies

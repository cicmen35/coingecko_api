# Coingecko api manager

## Overview
FastAPI application for managing cryptocurrency data in database with real-time updates from CoinGecko API.

## Features
- Create, read, update, and delete cryptocurrency entries
- Automatic validation of cryptocurrency symbols via CoinGecko API
- Real-time price and market cap data
- Daily automatic data refresh
- User-friendly Streamlit interface
- RESTful API with FastAPI

## Prerequisites
- Docker and Docker Compose

## Installation
Clone the repository
```bash
git clone https://github.com/cicmen35/coingecko_api.git
cd coingecko_api
```

## Running with Docker
The application is fully dockerized with separate containers for the API, Streamlit and PostgreSQL.

```bash
# Build the Docker images
docker-compose build

# Start the application
docker-compose up
```

This will start:
- FastAPI server at `http://localhost:8000`
- Streamlit UI at `http://localhost:8501`
- PostgreSQL database

To stop the application:
```bash
docker-compose down
```

To remove all data and start fresh:
```bash
docker-compose down -v
```

## API Documentation
Once the application is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure
- `app/`: FastAPI application logic
  - `app.py`: Main FastAPI application
  - `database.py`: Database models and connection
  - `services/`: Business logic and external API integration
- `streamlit/`: Streamlit user interface
  - `app.py`: Streamlit application
- `main.py`: Application entry point for running both FastAPI and Streamlit
- `Dockerfile`: Container configuration
- `docker-compose.yml`: Multi-container Docker configuration
- `requirements.txt`: Project dependencies

## Architecture
The application follows a microservices architecture with:
1. **API Service**: Handles data validation, database operations, and CoinGecko API integration
2. **UI Service**: Provides a user-friendly interface for interacting with the API
3. **Database Service**: Stores cryptocurrency data persistently


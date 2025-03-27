from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# Use environment variable for database URL, with a default fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://localhost/coingecko_api"
)

# Create engine with connection pooling disabled for better thread safety
engine = create_engine(
    DATABASE_URL, 
    poolclass=NullPool,  # Disable connection pooling
    pool_pre_ping=True   # Test connections before using them
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Base class for declarative models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

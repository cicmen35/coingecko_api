from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# Database Configuration
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

# Base class for declarative models
Base = declarative_base()

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CryptocurrencyDB(Base):
    """
    SQLAlchemy model for storing cryptocurrency information
    """
    __tablename__ = "cryptocurrencies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    symbol = Column(String, unique=True, index=True)
    current_price = Column(Float)
    market_cap = Column(Float)
    coingecko_id = Column(String, unique=True)
    last_updated = Column(Float, nullable=True)  

    def __repr__(self):
        return f"<Cryptocurrency(name='{self.name}', symbol='{self.symbol}', price={self.current_price})>"

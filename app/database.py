from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@db:5432/coingecko_api"
)


engine = create_engine(
    DATABASE_URL, 
    poolclass=NullPool,  
    pool_pre_ping=True   
)

Base = declarative_base()

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

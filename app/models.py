from sqlalchemy import Column, Integer, String, Float
from .database import Base

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
    last_updated = Column(Float, nullable=True)  # Timestamp of last update

    def __repr__(self):
        return f"<Cryptocurrency(name='{self.name}', symbol='{self.symbol}', price={self.current_price})>"

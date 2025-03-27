from pydantic import BaseModel, Field, validator
from typing import Optional, List

class CryptocurrencyBase(BaseModel):
    """
    Base model for cryptocurrency data validation
    """
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    current_price: float = Field(..., gt=0)
    market_cap: float = Field(..., gt=0)

    @validator('symbol')
    def validate_symbol(cls, symbol):
        """
        Convert symbol to lowercase for consistency
        """
        return symbol.lower()

class CryptocurrencyCreate(CryptocurrencyBase):
    """
    Model for creating a new cryptocurrency
    """
    pass

class CryptocurrencyUpdate(CryptocurrencyBase):
    """
    Model for updating an existing cryptocurrency
    Allows partial updates with optional fields
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    current_price: Optional[float] = Field(None, gt=0)
    market_cap: Optional[float] = Field(None, gt=0)

    class Config:
        extra = "allow"

class CryptocurrencyResponse(CryptocurrencyBase):
    """
    Model for returning cryptocurrency data from database
    """
    id: int
    coingecko_id: Optional[str]
    last_updated: Optional[float]

    class Config:
        orm_mode = True

class CryptocurrencyListResponse(BaseModel):
    """
    Model for returning a list of cryptocurrency data from database
    """
    data: List[CryptocurrencyResponse]

    class Config:
        extra = "allow"
        orm_mode = True

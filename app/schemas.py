from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class CryptocurrencyBase(BaseModel):
    """Base model for cryptocurrency data validation."""
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    coingecko_id: Optional[str] = None

class CryptocurrencyCreate(BaseModel):
    """Model for creating a new cryptocurrency
    Supports both CoinGecko and custom cryptocurrencies
    """
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)   
    coingecko_id: Optional[str] = None
    current_price: Optional[float] = Field(None, gt=0)
    market_cap: Optional[float] = Field(None, gt=0)

    @field_validator('symbol')
    def uppercase_symbol(cls, symbol):
        """Convert symbol to uppercase.
        
        :param symbol: str, cryptocurrency symbol.
        :return: str, uppercase cryptocurrency symbol.
        """
        return symbol.upper()

    @field_validator('current_price', 'market_cap', always=True)
    def validate_custom_crypto(cls, v, values):
        """Validate price and market cap for custom cryptocurrencies.
        
        :param v: float, current price or market cap.
        :param values: dict, other cryptocurrency attributes.
        :return: float, validated price or market cap.
        :raises ValueError: if custom cryptocurrency is missing price or market cap.
        """
        
        if not values.get('coingecko_id'):
            if v is None:
                raise ValueError("Custom cryptocurrencies must provide current price and market cap")
        return v

    class Config:
        """Pydantic configuration."""
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Bitcoin",
                "symbol": "BTC",
                "coingecko_id": "bitcoin",  
                "current_price": 50000,  
                "market_cap": 1000000000  
            }
        }

class CryptocurrencyUpdate(BaseModel):
    """Model for updating an existing cryptocurrency. 
    Allows partial updates with optional fields."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    current_price: Optional[float] = Field(None, gt=0)
    market_cap: Optional[float] = Field(None, gt=0)

    class Config:
        extra = "allow"

class CryptocurrencyResponse(BaseModel):
    """Model for returning cryptocurrency data from database."""
    id: int
    name: str
    symbol: str
    coingecko_id: Optional[str]
    current_price: Optional[float]
    market_cap: Optional[float]
    last_updated: Optional[float]

    class Config:
        orm_mode = True

class CryptocurrencyListResponse(BaseModel):
    """Model for returning a list of cryptocurrency data from database."""    
    data: List[CryptocurrencyResponse]

    class Config:
        extra = "allow"
        orm_mode = True

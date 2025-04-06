from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from typing import Optional, Dict
import time
    
from app.database import engine, Base, get_db, CryptocurrencyDB
from app.schemas import CryptocurrencyCreate, CryptocurrencyUpdate, CryptocurrencyResponse
from app.services.create_api_service import CoinGeckoService

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cryptocurrency API", 
    description="CRUD operations for cryptocurrency records"
)

@app.get("/health", status_code=200)
def health_check():
    """Health check endpoint for container healthchecks.
    
    :return: Dict with status information
    """
    return {"status": "healthy"}

def validate_cryptocurrency_with_coingecko(symbol: str) -> Optional[Dict]:
    """Validate cryptocurrency symbol using CoinGecko API.

    :param symbol: str, cryptocurrency symbol to validate.
    :return: CoinGecko cryptocurrency details if valid, None otherwise.
    """
    service = CoinGeckoService()
    return service.validate_cryptocurrency(symbol)

def auto_refresh_cryptocurrencies() -> None:
    """Automatically refresh cryptocurrency data in the database.

    :return: None
    """
    logger.info("Starting automatic cryptocurrency data refresh")
    db = next(get_db())
    
    try:
        cryptocurrencies = db.query(CryptocurrencyDB).all()
        
        for crypto in cryptocurrencies:
            try:
                if crypto.coingecko_id:
                    service = CoinGeckoService()
                    details = service.get_cryptocurrency_details(crypto.coingecko_id)
                    
                    if details:
                        crypto.current_price = details.get('current_price')
                        crypto.market_cap = details.get('market_cap')
                        crypto.last_updated = time.time()
                        
                        db.commit()
                        logger.info(f"Updated {crypto.symbol} with new details")
            
            except Exception as e:
                logger.error(f"Error updating {crypto.symbol}: {e}")
                db.rollback()
        
        logger.info("Cryptocurrency data refresh completed")
    
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(
    auto_refresh_cryptocurrencies, 
    IntervalTrigger(hours=24)  # run every 24 hours
)

@app.on_event("startup")
async def startup_event() -> None:
    """Start the background scheduler when the application starts.

    :return: None
    """
    scheduler.start()
    logger.info("Cryptocurrency auto-refresh scheduler started")

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Shutdown the background scheduler when the application stops.

    :return: None
    """
    scheduler.shutdown()
    logger.info("Cryptocurrency auto-refresh scheduler stopped")

@app.post("/cryptocurrencies/", response_model=CryptocurrencyResponse)
def create_cryptocurrency(
    cryptocurrency: CryptocurrencyCreate, 
    db: Session = Depends(get_db)
) -> CryptocurrencyDB:
    """Create a new cryptocurrency.

    :param cryptocurrency: CryptocurrencyCreate, cryptocurrency details.
    :param db: Session, database session.
    :return: CryptocurrencyDB, created cryptocurrency.
    """
    try:
        if not cryptocurrency.coingecko_id:
            if not (cryptocurrency.current_price and cryptocurrency.market_cap):
                raise HTTPException(
                    status_code=400, 
                    detail="Custom cryptocurrencies must provide current price and market cap"
                )
            
            new_crypto = CryptocurrencyDB(
                name=cryptocurrency.name,
                symbol=cryptocurrency.symbol,
                current_price=cryptocurrency.current_price,
                market_cap=cryptocurrency.market_cap
            )
        else:
            service = CoinGeckoService()
            validated_crypto = service.validate_cryptocurrency(
                symbol=cryptocurrency.symbol, 
                current_price=cryptocurrency.current_price, 
                market_cap=cryptocurrency.market_cap
            )
            
            if not validated_crypto:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cryptocurrency symbol {cryptocurrency.symbol} not found or invalid"
                )
            
            existing_crypto = db.query(CryptocurrencyDB).filter(
                (CryptocurrencyDB.symbol == validated_crypto['symbol']) | 
                (CryptocurrencyDB.name == validated_crypto['name'])
            ).first()
            
            if existing_crypto:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cryptocurrency with symbol {validated_crypto['symbol']} already exists"
                )
            
            new_crypto = CryptocurrencyDB(
                name=validated_crypto['name'],
                symbol=validated_crypto['symbol'],
                coingecko_id=validated_crypto.get('coingecko_id'),
                current_price=validated_crypto['current_price'],
                market_cap=validated_crypto['market_cap']
            )
        
        db.add(new_crypto)
        db.commit()
        db.refresh(new_crypto)
        
        return new_crypto
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating cryptocurrency: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/cryptocurrencies/", response_model=list[CryptocurrencyResponse])
def list_cryptocurrencies(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
) -> list[CryptocurrencyDB]:
    """Retrieve a list of cryptocurrencies with optional pagination.

    :param skip: int, number of records to skip.
    :param limit: int, number of records to return.
    :param db: Session, database session.
    :return: list[CryptocurrencyDB], list of cryptocurrencies.
    """
    cryptocurrencies = db.query(CryptocurrencyDB).offset(skip).limit(limit).all()
    return cryptocurrencies

@app.get("/cryptocurrencies/{cryptocurrency_id}", response_model=CryptocurrencyResponse)
def get_cryptocurrency(
    cryptocurrency_id: int, 
    db: Session = Depends(get_db)
) -> CryptocurrencyDB:
    """Retrieve a specific cryptocurrency by its ID.

    :param cryptocurrency_id: int, ID of the cryptocurrency.
    :param db: Session, database session.
    :return: CryptocurrencyDB, cryptocurrency.
    """
    cryptocurrency = db.query(CryptocurrencyDB).filter(CryptocurrencyDB.id == cryptocurrency_id).first()
    
    if not cryptocurrency:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    
    return cryptocurrency

@app.put("/cryptocurrencies/{cryptocurrency_id}", response_model=CryptocurrencyResponse)
def update_cryptocurrency(
    cryptocurrency_id: int, 
    cryptocurrency: CryptocurrencyUpdate, 
    db: Session = Depends(get_db)
) -> CryptocurrencyDB:
    """Update an existing cryptocurrency.

    :param cryptocurrency_id: int, ID of the cryptocurrency.
    :param cryptocurrency: CryptocurrencyUpdate, updated cryptocurrency details.
    :param db: Session, database session.
    :return: CryptocurrencyDB, updated cryptocurrency.
    """
    db_crypto = db.query(CryptocurrencyDB).filter(CryptocurrencyDB.id == cryptocurrency_id).first()
    
    if not db_crypto:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    
    if cryptocurrency.name:
        existing_name = db.query(CryptocurrencyDB).filter(
            (CryptocurrencyDB.name == cryptocurrency.name) & 
            (CryptocurrencyDB.id != cryptocurrency_id)
        ).first()
        if existing_name:
            raise HTTPException(status_code=400, detail="Cryptocurrency name already exists")
    
    if cryptocurrency.symbol:
        existing_symbol = db.query(CryptocurrencyDB).filter(
            (CryptocurrencyDB.symbol == cryptocurrency.symbol) & 
            (CryptocurrencyDB.id != cryptocurrency_id)
        ).first()
        if existing_symbol:
            raise HTTPException(status_code=400, detail="Cryptocurrency symbol already exists")
    
    update_data = cryptocurrency.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_crypto, key, value)
    
    db.commit()
    db.refresh(db_crypto)
    return db_crypto

@app.delete("/cryptocurrencies/{cryptocurrency_id}", response_model=CryptocurrencyResponse)
def delete_cryptocurrency(
    cryptocurrency_id: int, 
    db: Session = Depends(get_db)
) -> CryptocurrencyDB:
    """Delete a specific cryptocurrency by its ID.

    :param cryptocurrency_id: int, ID of the cryptocurrency.
    :param db: Session, database session.
    :return: CryptocurrencyDB, deleted cryptocurrency.
    """
    db_crypto = db.query(CryptocurrencyDB).filter(CryptocurrencyDB.id == cryptocurrency_id).first()
    
    if not db_crypto:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    
    db.delete(db_crypto)
    db.commit()
    
    return db_crypto

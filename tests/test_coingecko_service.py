from app.services.coingecko_service import CoinGeckoService

def test_validate_cryptocurrency_valid_symbol():
    """
    Test validation of a valid cryptocurrency symbol
    """
    # Test with a well-known cryptocurrency symbol
    result = CoinGeckoService.validate_cryptocurrency('btc')
    
    assert result is not None, "Validation failed for BTC"
    assert 'name' in result, "Name not found in result"
    assert 'symbol' in result, "Symbol not found in result"
    assert 'current_price' in result, "Current price not found in result"
    assert 'market_cap' in result, "Market cap not found in result"
    assert result['symbol'] == 'BTC', "Symbol not converted to uppercase"

def test_validate_cryptocurrency_invalid_symbol():
    """
    Test validation of an invalid cryptocurrency symbol
    """
    result = CoinGeckoService.validate_cryptocurrency('nonexistent_crypto')
    
    assert result is None, "Validation should return None for invalid symbol"

def test_get_top_cryptocurrencies():
    """
    Test fetching top cryptocurrencies
    """
    # Test default limit
    top_coins = CoinGeckoService.get_top_cryptocurrencies()
    
    assert isinstance(top_coins, list), "Result should be a list"
    assert len(top_coins) > 0, "Should return at least one cryptocurrency"
    
    # Check first coin structure
    first_coin = top_coins[0]
    assert 'name' in first_coin, "Coin name missing"
    assert 'symbol' in first_coin, "Coin symbol missing"
    assert 'current_price' in first_coin, "Current price missing"
    assert 'market_cap' in first_coin, "Market cap missing"
    assert 'coingecko_id' in first_coin, "CoinGecko ID missing"

def test_get_top_cryptocurrencies_limit():
    """
    Test fetching top cryptocurrencies with custom limit
    """
    # Test custom limit
    top_5_coins = CoinGeckoService.get_top_cryptocurrencies(limit=5)
    
    assert len(top_5_coins) == 5, "Should return exactly 5 cryptocurrencies"

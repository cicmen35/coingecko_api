import requests
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class CoinGeckoService:
    """Service for interacting with CoinGecko API."""
    BASE_URL = "https://api.coingecko.com/api/v3"

    def _validate_cryptocurrency(self, symbol: str, current_price: Optional[float] = None, market_cap: Optional[float] = None) -> Optional[Dict]:
        """Validate cryptocurrency symbol and fetch details from CoinGecko

        :param symbol: str, cryptocurrency symbol.
        :param current_price: float, optional, user-provided current price.
        :param market_cap: float, optional, user-provided market cap.
        :return: Dict with cryptocurrency details or None
        """
        try:
            search_url = f"{self.BASE_URL}/search?query={symbol}"
            response = requests.get(search_url)
            response.raise_for_status()
            
            search_results = response.json()
            
            coins = search_results.get('coins', [])
            for coin in coins:
                if coin['symbol'].lower() == symbol.lower():
                    coin_url = f"{self.BASE_URL}/coins/{coin['id']}"
                    coin_response = requests.get(coin_url)
                    coin_response.raise_for_status()
                    coin_details = coin_response.json()
                    
                    market_data = coin_details.get('market_data', {})
                    
                    coingecko_price = market_data.get('current_price', {}).get('usd', 0)
                    coingecko_market_cap = market_data.get('market_cap', {}).get('usd', 0)
                    
                    return {
                        'coingecko_id': coin['id'],
                        'name': coin_details.get('name', coin['name']),
                        'symbol': symbol.upper(),
                        'current_price': coingecko_price,
                        'market_cap': coingecko_market_cap,
                        'in_coingecko': True
                    }
            
            if current_price is not None and market_cap is not None:
                return {
                    'coingecko_id': None,
                    'name': symbol.upper(),
                    'symbol': symbol.upper(),
                    'current_price': current_price,
                    'market_cap': market_cap,
                    'in_coingecko': False
                }
            
            return None
        
        except requests.RequestException as e:
            logger.error(f"CoinGecko API request failed: {e}")
            
            if current_price is not None and market_cap is not None:
                return {
                    'coingecko_id': None,
                    'name': symbol.upper(),
                    'symbol': symbol.upper(),
                    'current_price': current_price,
                    'market_cap': market_cap,
                    'in_coingecko': False
                }
            
            return None

    def get_cryptocurrency_details(self, coingecko_id: str) -> Optional[Dict]:
        """Fetch detailed information about a cryptocurrency from CoinGecko.

        :param coingecko_id: str, CoinGecko ID of the cryptocurrency.
        :exception: requests.exceptions.RequestException if the request fails.
        :return: Dict with cryptocurrency details or None if retrieval fails.
        """
        try:
            coin_url = f"{self.BASE_URL}/coins/{coingecko_id}"
            coin_response = requests.get(coin_url)
            coin_response.raise_for_status()
            coin_details = coin_response.json()
            
            market_data = coin_details.get('market_data', {})
            
            return {
                'name': coin_details.get('name'),
                'current_price': market_data.get('current_price', {}).get('usd', 0),
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'last_updated': market_data.get('last_updated')
            }
        
        except requests.RequestException as e:
            logger.error(f"CoinGecko API request failed: {e}")
            return None

    def get_top_cryptocurrencies(self, limit: int = 10) -> List[Dict]:
        """Retrieve top cryptocurrencies by market cap from CoinGecko.

        :param limit: int, number of top cryptocurrencies to retrieve.
        :return: List of dictionaries containing top cryptocurrency details.
        """
        markets_url = f"{self.BASE_URL}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': False
        }
        
        response = requests.get(markets_url, params=params)
        response.raise_for_status()
        top_coins = response.json()
        
        return [
            {
                'name': coin['name'],
                'symbol': coin['symbol'].upper(),
                'current_price': coin['current_price'],
                'market_cap': coin['market_cap'],
                'coingecko_id': coin['id']
            }
            for coin in top_coins
        ]

    def validate_cryptocurrency(self, symbol: str) -> Optional[Dict]:
        """Validate cryptocurrency symbol using CoinGecko API.

        :param symbol: str, cryptocurrency symbol to validate.
        :return: Dict with cryptocurrency details or None if validation fails.
        """
        return self._validate_cryptocurrency(symbol)

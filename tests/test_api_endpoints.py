import pytest
from fastapi import status

def test_create_cryptocurrency(test_client, test_db):
    """
    Test creating a new cryptocurrency
    """
    # Prepare test data for a known cryptocurrency
    crypto_data = {
        "name": "Bitcoin",
        "symbol": "BTC",
        "current_price": 50000,
        "market_cap": 1000000000
    }
    
    response = test_client.post("/cryptocurrencies/", json=crypto_data)
    
    assert response.status_code == status.HTTP_200_OK, "Failed to create cryptocurrency"
    
    created_crypto = response.json()
    assert created_crypto['name'] == crypto_data['name']
    assert created_crypto['symbol'] == crypto_data['symbol'].upper()

def test_create_duplicate_cryptocurrency(test_client, test_db):
    """
    Test preventing duplicate cryptocurrency creation
    """
    # First creation should succeed
    crypto_data = {
        "name": "Ethereum",
        "symbol": "ETH",
        "current_price": 3000,
        "market_cap": 500000000
    }
    
    first_response = test_client.post("/cryptocurrencies/", json=crypto_data)
    assert first_response.status_code == status.HTTP_200_OK
    
    # Second creation with same data should fail
    second_response = test_client.post("/cryptocurrencies/", json=crypto_data)
    assert second_response.status_code == status.HTTP_400_BAD_REQUEST

def test_list_cryptocurrencies(test_client, test_db):
    """
    Test listing cryptocurrencies
    """
    # Create some test cryptocurrencies
    test_cryptos = [
        {"name": "Bitcoin", "symbol": "BTC", "current_price": 50000, "market_cap": 1000000000},
        {"name": "Ethereum", "symbol": "ETH", "current_price": 3000, "market_cap": 500000000}
    ]
    
    for crypto in test_cryptos:
        test_client.post("/cryptocurrencies/", json=crypto)
    
    # List cryptocurrencies
    response = test_client.get("/cryptocurrencies/")
    
    assert response.status_code == status.HTTP_200_OK
    cryptos = response.json()
    
    assert len(cryptos) >= len(test_cryptos), "Should return at least created cryptocurrencies"

def test_get_cryptocurrency_by_id(test_client, test_db):
    """
    Test retrieving a specific cryptocurrency by ID
    """
    # Create a test cryptocurrency
    crypto_data = {
        "name": "Cardano",
        "symbol": "ADA",
        "current_price": 1.5,
        "market_cap": 50000000
    }
    
    create_response = test_client.post("/cryptocurrencies/", json=crypto_data)
    created_crypto = create_response.json()
    
    # Retrieve the cryptocurrency
    response = test_client.get(f"/cryptocurrencies/{created_crypto['id']}")
    
    assert response.status_code == status.HTTP_200_OK
    retrieved_crypto = response.json()
    
    assert retrieved_crypto['id'] == created_crypto['id']
    assert retrieved_crypto['name'] == crypto_data['name']

def test_delete_cryptocurrency(test_client, test_db):
    """
    Test deleting a cryptocurrency
    """
    # Create a test cryptocurrency
    crypto_data = {
        "name": "Solana",
        "symbol": "SOL",
        "current_price": 100,
        "market_cap": 75000000
    }
    
    create_response = test_client.post("/cryptocurrencies/", json=crypto_data)
    created_crypto = create_response.json()
    
    # Delete the cryptocurrency
    delete_response = test_client.delete(f"/cryptocurrencies/{created_crypto['id']}")
    
    assert delete_response.status_code == status.HTTP_200_OK
    
    # Try to retrieve the deleted cryptocurrency
    get_response = test_client.get(f"/cryptocurrencies/{created_crypto['id']}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

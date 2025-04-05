import streamlit as st
import requests
import pandas as pd
    
BASE_URL = "http://api:8000"

def create_cryptocurrency() -> None:
    """Create a new cryptocurrency entry in the database.

    :return: None, displays Streamlit notification about creation status.
    """
    st.header("Create cryptocurrency")
    
    with st.form("create_crypto_form"):
        name = st.text_input("Cryptocurrency Name")
        symbol = st.text_input("Symbol")
        current_price = st.number_input("Current Price", min_value=0.0, step=0.01)
        market_cap = st.number_input("Market Cap", min_value=0.0, step=1.0)
        
        submit_button = st.form_submit_button("Create Cryptocurrency")
        
        if submit_button:
            try:
                response = requests.post(
                    f"{BASE_URL}/cryptocurrencies/", 
                    json={
                        "name": name,
                        "symbol": symbol,
                        "current_price": current_price,
                        "market_cap": market_cap
                    }
                )
                
                if response.status_code == 200:
                    st.success(f"Cryptocurrency {name} created successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")

def list_cryptocurrencies() -> None:
    """List all cryptocurrencies from the database.

    :return: None, displays cryptocurrencies in Streamlit table.
    """
    st.header("List cryptocurrencies")
    
    try:
        response = requests.get(f"{BASE_URL}/cryptocurrencies/")
        
        if response.status_code == 200:
            cryptocurrencies = response.json()
            
            if not cryptocurrencies:
                st.info("No cryptocurrencies found. Create a cryptocurrency!")
                return
            
            df = pd.DataFrame(cryptocurrencies)
            
            st.dataframe(df)
            
            selected_crypto = st.selectbox(
                "Select cryptocurrency", 
                options=df['id'].tolist(),
                format_func=lambda x: df[df['id'] == x]['name'].values[0]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Update cryptocurrency"):
                    st.session_state.update_crypto_id = selected_crypto
                    st.rerun()
            
            with col2:
                if st.button("Delete cryptocurrency"):
                    delete_cryptocurrency(selected_crypto)
        
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

def update_cryptocurrency(crypto_id: int) -> None:
    """Update an existing cryptocurrency entry.

    :param crypto_id: int, ID of the cryptocurrency to update.
    :return: None, displays Streamlit notification about update status.
    """
    st.header("Update cryptocurrency")
    
    try:
        response = requests.get(f"{BASE_URL}/cryptocurrencies/{crypto_id}")
        
        if response.status_code == 200:
            crypto = response.json()
            
            with st.form("update_crypto_form"):
                name = st.text_input("Cryptocurrency name", value=crypto['name'])
                symbol = st.text_input("Symbol", value=crypto['symbol'])
                current_price = st.number_input(
                    "Current price", 
                    min_value=0.0, 
                    step=0.01, 
                    value=crypto['current_price']
                )
                market_cap = st.number_input(
                    "Market cap", 
                    min_value=0.0, 
                    step=1.0, 
                    value=crypto['market_cap']
                )
                
                submit_button = st.form_submit_button("Update cryptocurrency")
                
                if submit_button:
                    try:
                        update_response = requests.put(
                            f"{BASE_URL}/cryptocurrencies/{crypto_id}", 
                            json={
                                "name": name,
                                "symbol": symbol,
                                "current_price": current_price,
                                "market_cap": market_cap
                            }
                        )
                        
                        if update_response.status_code == 200:
                            st.success(f"Cryptocurrency {name} updated successfully!")
                            st.json(update_response.json())
                        else:
                            st.error(f"Error: {update_response.json().get('detail', 'Unknown error')}")
                    
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection error: {e}")
        
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")

def delete_cryptocurrency(crypto_id: int) -> None:
    """Delete a cryptocurrency entry from the database.

    :param crypto_id: int, ID of the cryptocurrency to delete.
    :return: None, displays Streamlit notification about deletion status.
    """
    try:
        response = requests.delete(f"{BASE_URL}/cryptocurrencies/{crypto_id}")
        
        if response.status_code == 200:
            st.success(f"Cryptocurrency deleted successfully!")
            st.json(response.json())
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")

def main() -> None:
    """Main Streamlit application entry point.

    :return: None, sets up Streamlit UI and navigation.
    """
    st.title("Cryptocurrency database manager")
    
    page = st.sidebar.selectbox(
        "Choose a page", 
        ["Create cryptocurrency", "List cryptocurrencies"]
    )
    
    if hasattr(st.session_state, 'update_crypto_id'):
        update_cryptocurrency(st.session_state.update_crypto_id)
        del st.session_state.update_crypto_id
    else:
        if page == "Create cryptocurrency":
            create_cryptocurrency()
        elif page == "List cryptocurrencies":
            list_cryptocurrencies()

if __name__ == "__main__":
    main()

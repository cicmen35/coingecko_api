#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

setup_venv() {
    echo -e "${YELLOW}Setting up virtual environment...${NC}"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
}

check_database() {
    echo -e "${YELLOW}Checking database connection...${NC}"
    
    createdb coingecko_api 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Database 'coingecko_api' created successfully.${NC}"
    else
        echo -e "${GREEN}Database already exists.${NC}"
    fi
}

start_application() {
    echo -e "${YELLOW}Starting CoinGecko API and Streamlit applications...${NC}"
    python main.py
}

main() {
    for cmd in python3 pip uvicorn createdb streamlit; do
        if ! command_exists "$cmd"; then
            echo -e "${RED}Error: $cmd is not installed.${NC}"
            exit 1
        fi
    done

    setup_venv
    check_database
    start_application
}

main

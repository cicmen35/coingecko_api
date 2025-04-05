import uvicorn
import multiprocessing
import subprocess
import signal
import time
import os
import psycopg2

def run_fastapi() -> None:
    """Run FastAPI application.

    :return: None, runs FastAPI application.
    """
    uvicorn.run(
        "app.app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )

def run_streamlit() -> None:
    """Run Streamlit application.

    :return: None, runs Streamlit application.
    """
    subprocess.run([
        "streamlit", "run", "streamlit/app.py", 
        "--server.port", "8501"
    ])

def wait_for_database() -> None:
    """Wait for the database to be ready.

    :return: None
    """
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/coingecko_api")
    
    # Extract connection parameters from the URL
    # Format: postgresql://user:password@host:port/dbname
    db_parts = db_url.replace("postgresql://", "").split("/")
    db_name = db_parts[1] if len(db_parts) > 1 else "postgres"
    conn_parts = db_parts[0].split("@")
    user_pass = conn_parts[0].split(":")
    host_port = conn_parts[1].split(":")
    
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    
    max_retries = 60  
    retry_interval = 3  
    
    print(f"Waiting for database at {host}:{port}...")
    for i in range(max_retries):
        try:
            # Try to connect to postgres database first if the actual DB doesn't exist yet
            try:
                conn = psycopg2.connect(
                    dbname=db_name,
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    connect_timeout=5  # Add connection timeout
                )
            except psycopg2.OperationalError as e:
                if "does not exist" in str(e):
                    # Try connecting to postgres database instead
                    conn = psycopg2.connect(
                        dbname="postgres",
                        user=user,
                        password=password,
                        host=host,
                        port=port,
                        connect_timeout=5
                    )
                    # Create the database if it doesn't exist
                    conn.autocommit = True
                    cursor = conn.cursor()
                    cursor.execute(f"CREATE DATABASE {db_name}")
                    cursor.close()
                    print(f"Created database {db_name}")
                else:
                    raise
                    
            conn.close()
            print("Database is ready!")
            return
        except psycopg2.OperationalError as e:
            print(f"Database not ready yet ({str(e)}), retrying in {retry_interval} seconds... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
    
    print("Failed to connect to the database after maximum retries")
    raise Exception("Database connection failed")

def main() -> None:
    """Run FastAPI and Streamlit applications concurrently.

    :return: None, runs applications concurrently.
    """
    # Wait for the database to be ready
    wait_for_database()
    
    multiprocessing.set_start_method('spawn')

    stop_event = multiprocessing.Event()

    def signal_handler(sig, frame):
        print("\nReceived interrupt signal. Stopping applications...")
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        fastapi_process = multiprocessing.Process(target=run_fastapi)
        streamlit_process = multiprocessing.Process(target=run_streamlit)

        fastapi_process.start()
        streamlit_process.start()

        while not stop_event.is_set():
            if not fastapi_process.is_alive() or not streamlit_process.is_alive():
                break
            stop_event.wait(1)

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        if fastapi_process.is_alive():
            fastapi_process.terminate()
        if streamlit_process.is_alive():
            streamlit_process.terminate()

        fastapi_process.join(timeout=5)
        streamlit_process.join(timeout=5)

        if fastapi_process.is_alive():
            fastapi_process.kill()
        if streamlit_process.is_alive():
            streamlit_process.kill()

if __name__ == "__main__":
    main()

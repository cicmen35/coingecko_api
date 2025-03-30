import uvicorn
import multiprocessing
import subprocess
import signal

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
        "streamlit", "run", "ui/streamlit_app.py", 
        "--server.port", "8501"
    ])

def main() -> None:
    """Run FastAPI and Streamlit applications concurrently.

    :return: None, runs applications concurrently.
    """
    # Use spawn method to avoid stdin issues
    multiprocessing.set_start_method('spawn')

    # Create event to signal processes to stop
    stop_event = multiprocessing.Event()

    # Create processes
    fastapi_process = multiprocessing.Process(target=run_fastapi)
    streamlit_process = multiprocessing.Process(target=run_streamlit)

    # Signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print("\nReceived interrupt signal. Stopping applications...")
        stop_event.set()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start processes
        fastapi_process.start()
        streamlit_process.start()

        # Wait for processes to complete or be interrupted
        while not stop_event.is_set():
            if not fastapi_process.is_alive() or not streamlit_process.is_alive():
                break
            stop_event.wait(1)  # Check every second

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Terminate processes if they are still running
        if fastapi_process.is_alive():
            fastapi_process.terminate()
        if streamlit_process.is_alive():
            streamlit_process.terminate()

        # Wait for processes to fully terminate
        fastapi_process.join(timeout=5)
        streamlit_process.join(timeout=5)

        # Force kill if still running
        if fastapi_process.is_alive():
            fastapi_process.kill()
        if streamlit_process.is_alive():
            streamlit_process.kill()

if __name__ == "__main__":
    main()

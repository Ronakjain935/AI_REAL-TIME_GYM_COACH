import os
import sys
import subprocess

def application(environ, start_response):
    """
    WSGI compatibility handler for production servers.
    """
    status = '200 OK'
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)
    return [b"<h1>Apna AI Gym Coach Streamlit Server</h1><p>Please access Streamlit via the configured server port.</p>"]

def main():
    port = os.environ.get("PORT", "8501")
    cmd = [
        sys.executable, "-m", "streamlit", "run", "main.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()

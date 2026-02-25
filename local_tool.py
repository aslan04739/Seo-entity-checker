#!/usr/bin/env python3
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import webview


ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "streamlit_app.py"
PORT = 8501
URL = f"http://127.0.0.1:{PORT}"

_streamlit_process = None


def is_port_open(host="127.0.0.1", port=PORT, timeout=0.5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def start_streamlit():
    """Start Streamlit server once and keep it running."""
    global _streamlit_process
    
    if _streamlit_process is not None:
        # Already running
        return
    
    if is_port_open():
        # Port already in use, don't start
        return
    
    log_path = Path("/tmp/seo_local_tool.log")
    with log_path.open("a", encoding="utf-8") as log_file:
        _streamlit_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(APP_FILE),
                "--server.headless=true",
                f"--server.port={PORT}",
            ],
            cwd=ROOT,
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
        )


def wait_for_server(max_wait_seconds=30):
    """Wait for Streamlit to become available."""
    attempts = int(max_wait_seconds / 0.5)
    for _ in range(attempts):
        if is_port_open():
            return True
        time.sleep(0.5)
    return False


def cleanup(signum=None, frame=None):
    """Clean up on exit."""
    global _streamlit_process
    if _streamlit_process:
        try:
            os.killpg(os.getpgid(_streamlit_process.pid), signal.SIGTERM)
        except Exception:
            pass
    sys.exit(0)


def main():
    # Setup signal handlers for cleanup
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    start_streamlit()
    
    if not wait_for_server():
        raise RuntimeError("Could not start Streamlit server")

    webview.create_window(
        "SEO Local Tool",
        URL,
        width=1400,
        height=900,
        min_size=(1000, 700),
        text_select=True,
    )
    webview.start()
    cleanup()


if __name__ == "__main__":
    main()
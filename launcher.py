"""Desktop launcher used to package Pulse as a Windows application."""

import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as streamlit_cli


def open_dashboard() -> None:
    """Open the local dashboard after the Streamlit server has started."""
    time.sleep(2)
    webbrowser.open_new("http://localhost:8501")


def main() -> None:
    bundle_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    app_file = bundle_dir / "app.py"
    threading.Thread(target=open_dashboard, daemon=True).start()
    sys.argv = [
        "streamlit",
        "run",
        str(app_file),
        "--server.headless=true",
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
    ]
    streamlit_cli.main()


if __name__ == "__main__":
    main()

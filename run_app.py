import subprocess
import sys
import os

if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

app_path = os.path.join(base_path, "app.py")

subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    app_path,
    "--server.headless=true"
])
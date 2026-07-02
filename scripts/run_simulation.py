#!/usr/bin/env python3
"""Launch the Streamlit GUI. The app must run under `streamlit run`,
so this script just wraps that invocation."""
import os
import subprocess
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gui_path = os.path.join(project_root, "app", "views", "gui.py")

if __name__ == "__main__":
    sys.exit(subprocess.call(
        [sys.executable, "-m", "streamlit", "run", gui_path],
        cwd=project_root,
    ))

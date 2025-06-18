#!/usr/bin/env python3
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.views.gui import main

if __name__ == "__main__":
    main() 
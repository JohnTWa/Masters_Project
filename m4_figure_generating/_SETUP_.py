import sys
import os

def set_directory():
    PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)

    print(PROJECT_DIR)
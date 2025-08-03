# game/__main__.py
from __future__ import annotations
import os
import sys

# Add the parent of this file's dir so "import game.*" works after unpack
APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from game.main import run  # noqa: E402

if __name__ == "__main__":
    run()

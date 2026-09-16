"""Vercel Serverless Function entry point for P45 Research Engine."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from p45_v27.webapp import Handler

class handler(Handler):
    """Vercel Serverless Python entrypoint inheriting from Handler."""
    pass

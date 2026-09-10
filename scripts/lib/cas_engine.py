#!/usr/bin/env python3
"""
scripts/lib/cas_engine.py

Backward-compatibility proxy. The canonical module now lives in lib.cas.cas_engine.
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from lib.cas.cas_engine import *

if __name__ == "__main__":
    main()

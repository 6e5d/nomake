import sys
from pathlib import Path

from .build import build_recurse

rebuild = False
if len(sys.argv) >= 3:
	rebuild = True
build_recurse(Path(sys.argv[1]).resolve(), 0, rebuild)

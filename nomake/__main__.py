import sys
from pathlib import Path

from .build import build_recurse

build_recurse(Path(sys.argv[1]).resolve(), 0)

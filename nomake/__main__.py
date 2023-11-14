import sys
from pathlib import Path

from .build import build_recurse
from .check import nomake_check

rebuild = False
path = sys.argv[1]
if len(sys.argv) >= 3:
	opt = sys.argv[2]
	if opt == "check":
		nomake_check(path)
		sys.exit()
	elif opt == "rebuild":
		rebuild = True
	else:
		raise Exception("check/rebuild/none")
build_recurse(Path(path).resolve(), 0, rebuild)

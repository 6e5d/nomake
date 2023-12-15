from pyltr import parse
from c3cpy.c3cc import C3cc
from c3cpy.preprocess import preprocess
from buildc.build import build as buildc
from gid import path2gid, gid2c
from subprocess import run

def build_c3(proj):
	j = parse(open(proj / "lib.c3").read())
	bs = preprocess(j, False)
	gid = path2gid(proj)
	gid_snake = gid2c(gid, "snake", True)
	c3cc = C3cc()
	with open(proj / f"build/{proj.name}.h", "w") as f:
		for b in bs:
			c3cc.build(b.data, True)
			s = c3cc.output()
			print(s, file = f, end = "")
	with open(proj / f"build/{proj.name}.c", "w") as f:
		print(f'#include "{proj.name}.h"', file = f)
		for b in bs:
			c3cc.build(b.data, False)
			s = c3cc.output()
			print(s, file = f)
	buildc(proj)

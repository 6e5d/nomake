import sys, os, shutil
import time
from pathlib import Path

from buildc.build import build as buildc
from project_type import project_type
from .order import build_deps, tsort
from .glsl import build_glsl
from .c3 import build_c3

done = set()

def read_deps(proj):
	deps = []
	path = proj / ".lpat/deps.txt"
	if path.exists():
		for line in open(path):
			line = line.strip()
			if not line:
				continue
			deps.append(line)
	return deps

def build_list(d, proj):
	deps = read_deps(proj)
	for proj2 in deps:
		build_list(d, proj2)
	d.append(proj)

def min2(x, y):
	if x == None:
		return y
	else:
		return min(x, y)

def max2(x, y):
	if x == None:
		return y
	else:
		return max(x, y)

def test_obsolete(p, ty):
	name = p.name
	eobj = None
	lsrc = None
	for parent, _dirs, files in os.walk(p):
		parent = Path(parent)
		for file in files:
			mt = (parent / file).stat().st_mtime
			if parent.is_relative_to(p / "build"):
				eobj = min2(eobj, mt)
			else:
				lsrc = max2(lsrc, mt)
	return lsrc, eobj

def build_list(proj):
	deps, rdeps = build_deps(proj)
	l = []
	for proj in reversed(tsort(deps, rdeps)):
		l.append(proj)
	print([x.name for x in l])

	# keep only first occurrence
	s = set()
	l2 = []
	for p in l:
		if p in s:
			continue
		s.add(p)
		l2.append(p)
	return deps, rdeps, l2

def build(proj, rebuild):
	deps, rdeps, l2 = build_list(proj)
	latest_src = dict()
	for p in l2:
		ty = project_type(p)
		lsrc, eobj = test_obsolete(p, ty)
		latest_src[p] = lsrc
		if rebuild or eobj == None or eobj <= lsrc:
			pass
		else:
			for dep in deps[p]:
				if eobj <= latest_src[dep]:
					break
			else:
				continue
		if ty not in ["c", "c3", "glsl"]:
			continue
		if (p / "build").exists():
			shutil.rmtree(p / "build")
		(p / "build").mkdir()
		t = time.time()
		match ty:
			case "c":
				buildc(p)
			case "glsl":
				build_glsl(p)
			case "c3":
				build_c3(p)
			case x:
				raise Exception(x)
		dt = time.time() - t
		print(p.name, f"{dt:.2f}")

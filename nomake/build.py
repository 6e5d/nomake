import sys, os
import time
from subprocess import run
from pathlib import Path

from .link_lookup import link_lookup
from .depinfo import Depinfo
from .order import build_deps, tsort
from . import cc

done = set()

ccc = cc.clang
#ccc = cc.gcc

def runner(cmd):
	if cmd:
		p = run(cmd)
		if p.returncode != 0:
			print(p.returncode, " ".join(cmd))
			sys.exit(1)

def build_cmd(proj, depinfo, obj, test, rebuild):
	Path("build").mkdir(exist_ok = True)
	cmd = ccc()
	name = proj.name
	# order is important
	if obj.suffix == ".so":
		cmd += ["-fPIC", "-shared"]
	else:
		cmd += ["-fPIE"]
	for c in depinfo.cfiles:
		cmd.append(str(Path(f"src/{c}").resolve()))
	if test:
		cmd.append("src/test.c")
	cmd += ["-o", str(obj)]
	links = []
	for dep in depinfo.deps:
		sopath = dep / "build" / f"lib{dep.name}.so"
		# test if sopath is real library(or virtual)
		if not sopath.is_file():
			continue
		cmd.append(str(sopath))
	for c in depinfo.sysdeps:
		links += link_lookup(c)
	cmd += list(set(links))
	return cmd

def build_list(d, proj):
	depinfo = Depinfo()
	depinfo.build(proj)
	for proj2 in depinfo.deps:
		build_list(d, proj2)
	d.append((proj, depinfo))

def getmtime(file):
	if file.exists():
		return file.stat().st_mtime
	else:
		return 0

def test_obsolete(p, v):
	name = p.name
	earliest = 1<<63;
	if v.objs[0]:
		file = p / f"build/{name}.elf"
		v.objs[0] = file
		earliest = min(getmtime(file), earliest)
	if v.objs[1]:
		file = p / f"build/lib{name}.so"
		v.objs[1] = file
		earliest = min(getmtime(file), earliest)
	if v.objs[2]:
		file = p / f"build/test.elf"
		v.objs[2] = file
		earliest = min(getmtime(file), earliest)
	if earliest < v.latest:
		return True
	return False

def build(proj, rebuild):
	deps, rdeps = build_deps(proj)
	l = []
	for proj in reversed(tsort(deps, rdeps)):
		depinfo = Depinfo()
		depinfo.build(proj)
		l.append((proj, depinfo))
	print([x[0].name for x in l])

	# keep only first occurrence
	s = set()
	l2 = []
	for p, v in l:
		if p in s:
			continue
		s.add(p)
		l2.append((p, v))

	for p, v in l2:
		# also overwrite obj
		if not test_obsolete(p, v) and not rebuild:
			continue
		t = time.time()
		sizes = 0
		for idx, obj in enumerate(v.objs):
			if obj == False:
				continue
			os.chdir(p)
			cmd = build_cmd(p, v, obj, idx == 2, True)
			runner(cmd)
			sizes += obj.stat().st_size
		dt = time.time() - t
		print(p.name, f"{dt:.2f}", sizes)

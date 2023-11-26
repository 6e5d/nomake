import sys, os
import time
from subprocess import run
from pathlib import Path

from .link_lookup import link_lookup
from .depinfo import Depinfo
from . import cc

done = set()

def runner(cmd):
	if cmd:
		p = run(cmd)
		if p.returncode != 0:
			print(p.returncode, " ".join(cmd))
			sys.exit(1)

def build_cmd(proj, depinfo, obj, test, rebuild):
	Path("target").mkdir(exist_ok = True)
	name = proj.name
	#cmd = cc.clang()
	cmd = cc.gcc()
	# order is important
	if obj.endswith(".so"):
		cmd += ["-fPIC", "-shared"]
	else:
		cmd += ["-fPIE"]
	cmd += ["-o", obj]
	for c in depinfo.cfiles:
		cmd.append(str(Path(f"src/{c}").resolve()))
	if test:
		cmd.append("src/test.c")
	links = []
	for dep in depinfo.deps:
		sopath = dep / "target" / f"lib{dep.name}.so"
		# test if sopath is real library(or virtual)
		if sopath.is_file():
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
		file = p / f"target/{name}.elf"
		v.objs[0] = file
		earliest = min(getmtime(file), earliest)
	if v.objs[1]:
		file = p / f"target/lib{name}.so"
		v.objs[1] = file
		earliest = min(getmtime(file), earliest)
	if v.objs[2]:
		file = p / f"target/test.elf"
		v.objs[2] = file
		earliest = min(getmtime(file), earliest)
	if earliest < v.latest:
		return True
	return False

def build(proj, depth, rebuild):
	l = []
	build_list(l, proj)

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
			cmd = build_cmd(p, v, str(obj), idx == 2, True)
			runner(cmd)
			sizes += obj.stat().st_size
		dt = time.time() - t
		print(p.name, f"{dt:.2f}", sizes)

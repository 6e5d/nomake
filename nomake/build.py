import sys, os
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
	name = proj.name
	cmd = cc.clang()
	if obj.endswith(".so"):
		cmd += ["-fPIE", "-shared"]
	cmd += ["-o", obj]
	for dep in depinfo.deps:
		sopath = dep / "target" / f"lib{dep.name}.so"
		# test if sopath is real library(or virtual)
		if sopath.is_file():
			cmd.append(str(sopath))
	for c in depinfo.cfiles:
		cmd.append(str(Path(f"src/{c}").resolve()))
	if test:
		cmd.append("src/test.c")
	links = []
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
		v.state = 2

def build_recurse(proj, depth, rebuild):
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
		test_obsolete(p, v)
		if rebuild:
			v.state = 2

	# find weak build
	for p, v in l2:
		if v.state > 0:
			continue
		for dep in v.deps:
			if [v for p, v in l2 if p == dep][0].state == 2:
				v.state = 1

	for p, v in l2:
		if v.state == 0:
			continue
		print(f"\x1b[3{v.state + 2}m{p.name}\x1b[0m")
		for idx, obj in enumerate(v.objs):
			if obj == False:
				continue
			os.chdir(p)
			cmd = build_cmd(p, v, str(obj), idx == 2, True)
			runner(cmd)

def __deprecated():
	if proj in done:
		return
	print(depth, "entering", proj.name)
	if not (proj / "src").is_dir():
		assert (proj / "include").is_dir()
	(proj / "target").mkdir(exist_ok = True)
	depinfo = Depinfo()
	depinfo.build(proj)
	for proj2 in depinfo.deps:
		build_recurse(proj2, depth + 1, rebuild)
	os.chdir(proj)
	build(proj, depinfo, rebuild)
	done.add(proj)

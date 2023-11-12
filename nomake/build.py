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

def build(proj, depinfo, rebuild):
	name = proj.name
	if "main.c" in depinfo.cfiles:
		obj = f"target/{name}.elf"
	else:
		obj = f"target/lib{name}.so"
	# test if project contains any c files, otherwise header only
	if depinfo.cfiles:
		cmd = build_cmd(proj, depinfo, obj, False, rebuild)
		print(obj, "argc", len(cmd))
		runner(cmd)
	test_file = proj / "src/test.c"
	if test_file.exists():
		obj = "target/test.elf"
		cmd = build_cmd(proj, depinfo, obj, True, rebuild)
		print("test argc", len(cmd))
		runner(cmd)

def build_cmd(proj, depinfo, obj, test, rebuild):
	name = proj.name
	cmd = cc.clang()
	if obj.endswith(".so"):
		cmd += ["-fPIE", "-shared"]
	if Path(proj / obj).exists():
		if not rebuild and \
			Path(proj / obj).stat().st_mtime > depinfo.latest:
			print("utd", obj)
			return []
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

def build_recurse(proj, depth, rebuild):
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

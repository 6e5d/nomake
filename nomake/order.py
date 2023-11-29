from project_type import project_type

def build_deps(root):
	queue = [root]
	deps = dict()
	rdeps = dict()
	while queue:
		proj = queue.pop()
		if proj in deps:
			continue
		deps[proj] = []
		if proj not in rdeps:
			rdeps[proj] = []
		if (proj / ".lpat/deps.txt").exists():
			for line in open(proj / ".lpat/deps.txt"):
				line = line.strip()
				if not line:
					break
				p2 = (proj / ".." / line).resolve()
				if project_type(p2) != "c":
					continue
				deps[proj].append(p2)
				if p2 not in rdeps:
					rdeps[p2] = []
				rdeps[p2].append(proj)
				queue.append(p2)
	return deps, rdeps

def print_deps(deps):
	for key, vals in deps.items():
		print(key.name, end = ":")
		for val in vals:
			print(end = f" {val.name}")
		print()

def tsort(deps, rdeps):
	l = []
	s = set([k for k, v in rdeps.items() if not v])
	while s:
		p = s.pop()
		l.append(p)
		for v in deps[p]:
			rdeps[v].remove(p)
			if not rdeps[v]:
				s.add(v)
	for k, v in rdeps.items():
		if v:
			raise Exception(k, v)
	return(l)
